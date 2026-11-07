import uuid
from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from apps.files.models import File
from apps.sharing.tests.helpers import make_file, make_user
from apps.uploads.models import Upload
from apps.uploads.storage import StoredObject, get_storage

from .helpers import complete, start_and_put, start_upload

PDF_BYTES = b"%PDF-1.4 brand brief"


@pytest.mark.django_db
def test_complete_creates_the_file(client: Client) -> None:
    user = make_user()
    upload_id = start_and_put(client, user, "Brand brief v2.pdf", PDF_BYTES, "application/pdf")

    response = complete(client, upload_id)

    assert response.status_code == 200
    data = response.json()["data"]
    file = File.objects.get(owner=user, name="Brand brief v2.pdf")
    assert data["id"] == str(file.id)
    assert data["access"] == "owner"
    assert data["permissions"] == ["view", "edit", "delete"]
    assert data["member_count"] == 1
    assert data["size_bytes"] == len(PDF_BYTES)
    assert data["mime_type"] == "application/pdf"
    assert get_storage().head(file.storage_key) == StoredObject(len(PDF_BYTES), "application/pdf")
    assert get_storage().head(f"uploads/{upload_id}") is None


@pytest.mark.django_db
def test_complete_before_bytes_arrive_is_409(client: Client) -> None:
    user = make_user()
    upload = start_upload(
        client, user, {"name": "a.pdf", "size_bytes": 3, "mime_type": "application/pdf"}
    ).json()["data"][0]

    response = complete(client, upload["id"])

    assert response.status_code == 409
    assert response.json()["errors"][0]["code"] == "upload_incomplete"
    assert not File.objects.exists()


@pytest.mark.django_db
def test_complete_with_different_size_is_409(client: Client) -> None:
    user = make_user()
    upload = start_upload(
        client, user, {"name": "a.pdf", "size_bytes": 10, "mime_type": "application/pdf"}
    ).json()["data"][0]
    client.put(upload["put_url"], data=b"short", content_type="application/pdf")

    response = complete(client, upload["id"])

    assert response.status_code == 409
    assert response.json()["errors"][0]["code"] == "upload_incomplete"


@pytest.mark.django_db
def test_complete_after_expiry_is_410(client: Client) -> None:
    user = make_user()
    upload_id = start_and_put(client, user, "a.pdf", PDF_BYTES, "application/pdf")
    Upload.objects.filter(id=upload_id).update(expires_at=timezone.now() - timedelta(seconds=1))

    response = complete(client, upload_id)

    assert response.status_code == 410
    assert response.json()["errors"][0]["code"] == "upload_expired"


@pytest.mark.django_db
def test_someone_elses_upload_is_404(client: Client) -> None:
    upload_id = start_and_put(client, make_user(), "a.pdf", PDF_BYTES, "application/pdf")
    client.force_login(make_user("test_other_user"))

    response = complete(client, upload_id)

    assert response.status_code == 404
    assert response.json()["errors"][0]["code"] == "not_found"


@pytest.mark.django_db
def test_unknown_upload_is_404(client: Client) -> None:
    client.force_login(make_user())

    assert complete(client, str(uuid.uuid4())).status_code == 404


@pytest.mark.django_db
def test_anonymous_is_401(client: Client) -> None:
    assert complete(client, str(uuid.uuid4())).status_code == 401


@pytest.mark.django_db
def test_complete_twice_returns_the_same_file_once(client: Client) -> None:
    user = make_user()
    upload_id = start_and_put(client, user, "a.pdf", PDF_BYTES, "application/pdf")
    first = complete(client, upload_id).json()["data"]

    second = complete(client, upload_id)

    assert second.status_code == 200
    assert second.json()["data"]["id"] == first["id"]
    assert File.objects.count() == 1


@pytest.mark.django_db
def test_name_taken_meanwhile_is_409_name_conflict(client: Client) -> None:
    user = make_user()
    upload_id = start_and_put(client, user, "a.pdf", PDF_BYTES, "application/pdf")
    make_file(user, "a.pdf")

    response = complete(client, upload_id)

    assert response.status_code == 409
    assert response.json()["errors"][0]["code"] == "name_conflict"
    assert File.objects.count() == 1
