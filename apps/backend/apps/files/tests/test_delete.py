from pathlib import Path

import pytest
from django.test import Client

from apps.files.models import File
from apps.sharing.models import Grant, ShareLink
from apps.sharing.tests.helpers import make_file, make_grant, make_link, make_user
from apps.uploads.storage import LocalBlobStorage

from .helpers import post_json


def delete(client: Client, file: File) -> object:
    return post_json(client, f"/api/v1/files/{file.id}/delete", {})


def store_bytes(file: File) -> Path:
    path = LocalBlobStorage().path_for(file.storage_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"hello")
    LocalBlobStorage.mime_path(path).write_text(file.mime_type)
    return path


@pytest.mark.django_db
def test_owner_deletes_file_links_grants_and_bytes(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    file = make_file(user, "notes.txt")
    make_grant(file, kate, make_link(file, user))
    path = store_bytes(file)
    client.force_login(user)

    response = delete(client, file)

    assert response.status_code == 204  # type: ignore[attr-defined]
    assert response.content == b""  # type: ignore[attr-defined]
    assert not File.objects.filter(id=file.id).exists()
    assert not ShareLink.objects.filter(file_id=file.id).exists()
    assert not Grant.objects.filter(file_id=file.id).exists()
    assert not path.exists()
    assert not LocalBlobStorage.mime_path(path).exists()


@pytest.mark.django_db
def test_grantee_with_delete_can_delete(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    file = make_file(user, "notes.txt")
    make_grant(file, kate, make_link(file, user, permissions=("view", "delete")))
    client.force_login(kate)

    assert delete(client, file).status_code == 204  # type: ignore[attr-defined]
    assert not File.objects.filter(id=file.id).exists()


@pytest.mark.django_db
def test_grantee_with_view_is_403(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    file = make_file(user, "notes.txt")
    make_grant(file, kate, make_link(file, user, permissions=("view", "edit")))
    client.force_login(kate)

    response = delete(client, file)

    assert response.status_code == 403  # type: ignore[attr-defined]
    assert response.json()["errors"][0]["code"] == "forbidden"  # type: ignore[attr-defined]
    assert File.objects.filter(id=file.id).exists()


@pytest.mark.django_db
def test_stranger_is_404(client: Client) -> None:
    file = make_file(make_user(), "notes.txt")
    client.force_login(make_user("test_other_user"))

    response = delete(client, file)

    assert response.status_code == 404  # type: ignore[attr-defined]
    assert response.json()["errors"][0]["code"] == "not_found"  # type: ignore[attr-defined]
