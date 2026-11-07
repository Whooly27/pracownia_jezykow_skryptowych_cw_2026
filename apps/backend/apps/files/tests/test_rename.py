import pytest
from django.test import Client

from apps.files.models import File
from apps.sharing.tests.helpers import make_file, make_grant, make_link, make_user

from .helpers import post_json


def rename(client: Client, file: File, name: str) -> object:
    return post_json(client, f"/api/v1/files/{file.id}/rename", {"name": name})


@pytest.mark.django_db
def test_owner_renames_and_modified_at_moves(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    before = file.modified_at
    client.force_login(user)

    response = rename(client, file, "  Notes 2026.txt ")

    assert response.status_code == 200  # type: ignore[attr-defined]
    data = response.json()["data"]  # type: ignore[attr-defined]
    assert data["name"] == "Notes 2026.txt"
    assert data["access"] == "owner"
    file.refresh_from_db()
    assert file.name == "Notes 2026.txt"
    assert file.modified_at > before


@pytest.mark.django_db
def test_same_name_is_fine(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    client.force_login(user)

    assert rename(client, file, "notes.txt").status_code == 200  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_grantee_with_edit_is_403(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    file = make_file(user, "notes.txt")
    make_grant(file, kate, make_link(file, user, permissions=("view", "edit")))
    client.force_login(kate)

    response = rename(client, file, "other.txt")

    assert response.status_code == 403  # type: ignore[attr-defined]
    assert response.json()["errors"][0]["code"] == "forbidden"  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_stranger_is_404(client: Client) -> None:
    file = make_file(make_user(), "notes.txt")
    client.force_login(make_user("test_other_user"))

    response = rename(client, file, "other.txt")

    assert response.status_code == 404  # type: ignore[attr-defined]
    assert response.json()["errors"][0]["message"] == (  # type: ignore[attr-defined]
        f"File {file.id} doesn't exist or you can't see it."
    )


@pytest.mark.django_db
def test_taken_name_is_409(client: Client) -> None:
    user = make_user()
    make_file(user, "taken.txt")
    file = make_file(user, "notes.txt")
    client.force_login(user)

    response = rename(client, file, "taken.txt")

    assert response.status_code == 409  # type: ignore[attr-defined]
    assert response.json()["errors"][0]["code"] == "name_conflict"  # type: ignore[attr-defined]
    file.refresh_from_db()
    assert file.name == "notes.txt"


@pytest.mark.django_db
def test_bad_name_lists_problems_422(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    client.force_login(user)

    response = rename(client, file, "x" * 256 + "/y.txt")

    assert response.status_code == 422  # type: ignore[attr-defined]
    assert len(response.json()["errors"]) == 2  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_extension_not_matching_type_is_415(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    client.force_login(user)

    response = rename(client, file, "notes.pdf")

    assert response.status_code == 415  # type: ignore[attr-defined]
    assert response.json()["errors"][0]["code"] == "unsupported_file_type"  # type: ignore[attr-defined]
