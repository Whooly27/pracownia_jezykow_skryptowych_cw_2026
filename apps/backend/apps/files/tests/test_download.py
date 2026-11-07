from datetime import datetime, timedelta

import pytest
from django.test import Client
from django.utils import timezone

from apps.files.models import File
from apps.sharing.tests.helpers import make_file, make_grant, make_link, make_user
from apps.uploads.storage import LocalBlobStorage

from .helpers import post_json

BODY = b"hello from notes"


def download(client: Client, file: File) -> object:
    return post_json(client, f"/api/v1/files/{file.id}/download", {})


def store_bytes(file: File) -> None:
    path = LocalBlobStorage().path_for(file.storage_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(BODY)
    LocalBlobStorage.mime_path(path).write_text(file.mime_type)


@pytest.mark.django_db
def test_owner_gets_a_url_valid_for_60_seconds(client: Client) -> None:
    user = make_user()
    file = make_file(user, "notes.txt")
    store_bytes(file)
    client.force_login(user)
    before = timezone.now()

    response = download(client, file)

    assert response.status_code == 200  # type: ignore[attr-defined]
    data = response.json()["data"]  # type: ignore[attr-defined]
    expires_at = datetime.fromisoformat(data["expires_at"])
    assert timedelta(seconds=55) < expires_at - before <= timedelta(seconds=60)
    got = client.get(data["url"])
    assert got.status_code == 200
    assert b"".join(got.streaming_content) == BODY  # type: ignore[attr-defined]
    assert 'filename="notes.txt"' in got["Content-Disposition"]
    assert got["Content-Type"] == "text/plain"


@pytest.mark.django_db
def test_grantee_with_view_gets_a_url(client: Client) -> None:
    user = make_user()
    kate = make_user("test_kate")
    file = make_file(user, "notes.txt")
    make_grant(file, kate, make_link(file, user))
    client.force_login(kate)

    assert download(client, file).status_code == 200  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_stranger_is_404(client: Client) -> None:
    file = make_file(make_user(), "notes.txt")
    client.force_login(make_user("test_other_user"))

    response = download(client, file)

    assert response.status_code == 404  # type: ignore[attr-defined]
    assert response.json()["errors"][0]["code"] == "not_found"  # type: ignore[attr-defined]
