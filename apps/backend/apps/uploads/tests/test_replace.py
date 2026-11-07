import uuid
from typing import Any

import pytest
from django.test import Client

from apps.files.models import File
from apps.sharing.models import Grant
from apps.sharing.tests.helpers import make_file, make_grant, make_link, make_user
from apps.uploads.storage import StoredObject, get_storage

from .helpers import complete, post_json

NEW_BYTES = b"brand new contents"


def replace(
    client: Client, file: File, size: int = len(NEW_BYTES), mime: str = "text/plain"
) -> Any:
    return post_json(
        client, f"/api/v1/files/{file.id}/replace", {"size_bytes": size, "mime_type": mime}
    )


@pytest.mark.django_db
def test_owner_can_replace_and_complete_keeps_id_and_name(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    old_modified = file.modified_at
    client.force_login(user)

    response = replace(client, file)
    assert response.status_code == 201
    upload = response.json()["data"]
    assert upload["name"] == "notes.txt"
    assert upload["put_headers"] == {"content-type": "text/plain"}
    assert (
        client.put(upload["put_url"], data=NEW_BYTES, content_type="text/plain").status_code == 200
    )

    done = complete(client, upload["id"])

    assert done.status_code == 200
    data = done.json()["data"]
    assert data["id"] == str(file.id)
    assert data["name"] == "notes.txt"
    assert data["size_bytes"] == len(NEW_BYTES)
    file.refresh_from_db()
    assert file.modified_at > old_modified
    assert get_storage().head(file.storage_key) == StoredObject(len(NEW_BYTES), "text/plain")
    assert File.objects.count() == 1


@pytest.mark.django_db
def test_grantee_with_edit_can_replace(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    file = make_file(user, "notes.txt")
    make_grant(file, kate, make_link(file, user, permissions=("view", "edit")))
    client.force_login(kate)

    response = replace(client, file)

    assert response.status_code == 201


@pytest.mark.django_db
def test_grantee_with_view_only_is_403(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    file = make_file(user, "notes.txt")
    make_grant(file, kate, make_link(file, user, permissions=("view",)))
    client.force_login(kate)

    response = replace(client, file)

    assert response.status_code == 403
    assert response.json()["errors"][0]["code"] == "forbidden"


@pytest.mark.django_db
def test_stranger_is_404(client: Client) -> None:
    file = make_file(make_user(), "notes.txt")
    client.force_login(make_user("test_other_user"))

    assert replace(client, file).status_code == 404


@pytest.mark.django_db
def test_unknown_file_is_404(client: Client) -> None:
    client.force_login(make_user())

    response = post_json(
        client,
        f"/api/v1/files/{uuid.uuid4()}/replace",
        {"size_bytes": 1, "mime_type": "text/plain"},
    )

    assert response.status_code == 404
    assert response.json()["errors"][0]["code"] == "not_found"


@pytest.mark.django_db
def test_wrong_type_is_415(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    client.force_login(user)

    response = replace(client, file, mime="application/pdf")

    assert response.status_code == 415
    assert response.json()["errors"][0]["code"] == "unsupported_file_type"


@pytest.mark.django_db
def test_too_large_is_413(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    client.force_login(user)

    response = replace(client, file, size=26214401)

    assert response.status_code == 413
    assert response.json()["errors"][0]["code"] == "file_too_large"


@pytest.mark.django_db
def test_bad_size_is_422(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    client.force_login(user)

    assert replace(client, file, size=0).status_code == 422


@pytest.mark.django_db
def test_complete_after_losing_edit_is_403(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    file = make_file(user, "notes.txt")
    make_grant(file, kate, make_link(file, user, permissions=("view", "edit")))
    client.force_login(kate)
    upload = replace(client, file).json()["data"]
    client.put(upload["put_url"], data=NEW_BYTES, content_type="text/plain")
    Grant.objects.filter(user=kate).delete()

    response = complete(client, upload["id"])

    assert response.status_code == 404
    assert file.size_bytes == File.objects.get(id=file.id).size_bytes


@pytest.mark.django_db
def test_complete_after_dropping_to_view_is_403(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    file = make_file(user, "notes.txt")
    edit_grant = make_grant(file, kate, make_link(file, user, permissions=("view", "edit")))
    make_grant(file, kate, make_link(file, user, permissions=("view",)))
    client.force_login(kate)
    upload = replace(client, file).json()["data"]
    client.put(upload["put_url"], data=NEW_BYTES, content_type="text/plain")
    edit_grant.delete()

    response = complete(client, upload["id"])

    assert response.status_code == 403
    assert response.json()["errors"][0]["code"] == "forbidden"


@pytest.mark.django_db
def test_complete_after_file_deleted_is_404(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    client.force_login(user)
    upload = replace(client, file).json()["data"]
    client.put(upload["put_url"], data=NEW_BYTES, content_type="text/plain")
    file.delete()

    response = complete(client, upload["id"])

    assert response.status_code == 404
    assert response.json()["errors"][0]["code"] == "not_found"


@pytest.mark.django_db
def test_repeated_complete_after_losing_access_is_404(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    file = make_file(user, "notes.txt")
    make_grant(file, kate, make_link(file, user, permissions=("view", "edit")))
    client.force_login(kate)
    upload = replace(client, file).json()["data"]
    client.put(upload["put_url"], data=NEW_BYTES, content_type="text/plain")
    assert complete(client, upload["id"]).status_code == 200
    Grant.objects.filter(user=kate).delete()

    response = complete(client, upload["id"])

    assert response.status_code == 404
    assert response.json()["errors"][0]["code"] == "not_found"
