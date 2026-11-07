from datetime import timedelta

import pytest
from django.test import Client

from apps.files.models import File
from apps.sharing.tests.helpers import make_file, make_grant, make_link, make_user

from .helpers import list_files, names


@pytest.mark.django_db
def test_own_files_sorted_by_name_with_policy(client: Client) -> None:
    user = make_user()
    make_file(user, "b.txt")
    make_file(user, "a.txt")
    make_file(make_user("test_other_user"), "c.txt")

    response = list_files(client, user)

    assert response.status_code == 200
    data = response.json()["data"]
    assert names(response) == ["a.txt", "b.txt"]
    assert data["has_more"] is False
    assert data["upload_policy"]["max_file_bytes"] == 26214400
    assert data["items"][0]["access"] == "owner"


@pytest.mark.django_db
def test_shared_with_me_excludes_own_files_and_has_no_policy(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    make_file(kate, "mine.txt")
    shared = make_file(user, "shared.txt")
    make_grant(shared, kate, make_link(shared, user))
    make_grant(shared, kate, make_link(shared, user, permissions=("view", "edit")))
    make_file(user, "private.txt")

    response = list_files(client, kate, shared_with_me="true")

    assert names(response) == ["shared.txt"]
    assert response.json()["data"]["upload_policy"] is None
    assert response.json()["data"]["items"][0]["permissions"] == ["view", "edit"]


@pytest.mark.django_db
def test_shared_by_me_lists_only_files_with_grants(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    shared = make_file(user, "shared.txt")
    make_grant(shared, kate, make_link(shared, user))
    linked_only = make_file(user, "linked.txt")
    make_link(linked_only, user)
    make_file(user, "private.txt")

    response = list_files(client, user, shared_by_me="true")

    assert names(response) == ["shared.txt"]
    assert response.json()["data"]["items"][0]["is_shared"] is True


@pytest.mark.django_db
def test_search_matches_own_and_shared_case_insensitively(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    make_file(kate, "Budget 2027.xlsx")
    shared = make_file(user, "Q4 budget.xls")
    make_grant(shared, kate, make_link(shared, user))
    make_file(user, "Travel budget.csv")
    make_file(kate, "notes.txt")

    response = list_files(client, kate, q="BUDG")

    assert names(response) == ["Budget 2027.xlsx", "Q4 budget.xls"]


@pytest.mark.django_db
def test_search_shorter_than_2_is_422(client: Client) -> None:
    response = list_files(client, make_user(), q="b")

    assert response.status_code == 422
    assert response.json()["errors"][0]["code"] == "validation_failed"


@pytest.mark.django_db
def test_two_filters_is_422(client: Client) -> None:
    response = list_files(client, make_user(), shared_with_me="true", q="ab")

    assert response.status_code == 422


@pytest.mark.django_db
def test_bad_sort_order_and_limit_list_three_problems(client: Client) -> None:
    response = list_files(client, make_user(), sort="size", order="up", limit="0")

    assert response.status_code == 422
    assert len(response.json()["errors"]) == 3
    assert {e["code"] for e in response.json()["errors"]} == {"validation_failed"}


@pytest.mark.django_db
def test_pages_follow_each_other_without_gaps(client: Client) -> None:
    user = make_user()
    for name in ["e", "d", "c", "b", "a"]:
        make_file(user, f"{name}.txt")

    first = list_files(client, user, limit=2)
    second = list_files(client, user, limit=2, after=first.json()["data"]["items"][-1]["id"])
    third = list_files(client, user, limit=2, after=second.json()["data"]["items"][-1]["id"])

    assert names(first) == ["a.txt", "b.txt"]
    assert names(second) == ["c.txt", "d.txt"]
    assert names(third) == ["e.txt"]
    assert [r.json()["data"]["has_more"] for r in (first, second, third)] == [True, True, False]


@pytest.mark.django_db
def test_same_name_from_two_owners_paginate_cleanly(client: Client) -> None:
    kate = make_user("test_kate")
    seen: list[str] = []
    for owner_name in ("test_user", "test_other_user"):
        owner = make_user(owner_name)
        file = make_file(owner, "a.txt")
        make_grant(file, kate, make_link(file, owner))

    after = None
    for _ in range(3):
        params = {"shared_with_me": "true", "limit": 1}
        if after:
            params["after"] = after
        page = list_files(client, kate, **params).json()["data"]
        seen += [item["id"] for item in page["items"]]
        if not page["has_more"]:
            break
        after = page["items"][-1]["id"]

    assert len(seen) == 2
    assert len(set(seen)) == 2


@pytest.mark.django_db
def test_after_outside_the_list_is_invalid_after(client: Client) -> None:
    user = make_user()
    make_file(user, "a.txt")
    foreign = make_file(make_user("test_other_user"), "b.txt")

    response = list_files(client, user, after=str(foreign.id))

    assert response.status_code == 422
    assert response.json()["errors"][0]["code"] == "invalid_after"


@pytest.mark.django_db
def test_sort_by_modified_at_desc(client: Client) -> None:
    user = make_user()
    old = make_file(user, "old.txt")
    new = make_file(user, "new.txt")
    File.objects.filter(id=old.id).update(modified_at=new.modified_at - timedelta(days=1))

    response = list_files(client, user, sort="modified_at", order="desc")

    assert names(response) == ["new.txt", "old.txt"]


@pytest.mark.django_db
def test_anonymous_is_401(client: Client) -> None:
    assert client.get("/api/v1/files").status_code == 401
