import pytest
from django.test import Client

from apps.files.models import File
from apps.sharing.models import Grant
from apps.sharing.tests.helpers import make_file, make_grant, make_link, make_user

from .helpers import post_json


def remove_access(client: Client, file: File) -> object:
    return post_json(client, f"/api/v1/files/{file.id}/remove-access", {})


@pytest.mark.django_db
def test_grantee_removes_all_their_grants_only(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    jo = make_user("test_jo")
    file = make_file(user, "notes.txt")
    make_grant(file, kate, make_link(file, user))
    make_grant(file, kate, make_link(file, user, permissions=("view", "edit")))
    make_grant(file, jo, make_link(file, user))
    client.force_login(kate)

    response = remove_access(client, file)

    assert response.status_code == 204  # type: ignore[attr-defined]
    assert Grant.objects.filter(file=file, user=kate).count() == 0
    assert Grant.objects.filter(file=file, user=jo).count() == 1
    assert File.objects.filter(id=file.id).exists()


@pytest.mark.django_db
def test_owner_is_404(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    client.force_login(user)

    response = remove_access(client, file)

    assert response.status_code == 404  # type: ignore[attr-defined]
    assert response.json()["errors"][0]["message"] == "The file isn't shared with you."  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_stranger_is_404(client: Client) -> None:
    file = make_file(make_user(), "notes.txt")
    client.force_login(make_user("test_other_user"))

    assert remove_access(client, file).status_code == 404  # type: ignore[attr-defined]
