from datetime import timedelta
from pathlib import Path

import pytest
from django.test import Client
from django.utils import timezone

from apps.uploads.storage import StoredObject, get_storage

PDF = b"%PDF-1.4 hello"


def put_url(key: str = "uploads/abc", size: int = len(PDF), minutes: int = 15) -> str:
    return get_storage().put_url(
        key, "application/pdf", size, timezone.now() + timedelta(minutes=minutes)
    )


def test_put_then_head_returns_size_and_mime(client: Client) -> None:
    response = client.put(put_url(), data=PDF, content_type="application/pdf")

    assert response.status_code == 200
    assert get_storage().head("uploads/abc") == StoredObject(len(PDF), "application/pdf")


def test_head_of_missing_key_is_none() -> None:
    assert get_storage().head("uploads/nope") is None


def test_put_with_bad_token_is_403(client: Client, blob_root: Path) -> None:
    response = client.put(
        "/api/v1/_blob/uploads/abc?token=forged", data=PDF, content_type="application/pdf"
    )

    assert response.status_code == 403
    assert list(blob_root.iterdir()) == []


def test_put_to_a_key_other_than_the_signed_one_is_403(client: Client) -> None:
    url = put_url("uploads/abc").replace("uploads/abc", "uploads/other")

    response = client.put(url, data=PDF, content_type="application/pdf")

    assert response.status_code == 403
    assert get_storage().head("uploads/other") is None


def test_put_with_wrong_content_type_is_400_and_stores_nothing(client: Client) -> None:
    response = client.put(put_url(), data=PDF, content_type="image/png")

    assert response.status_code == 400
    assert get_storage().head("uploads/abc") is None


def test_put_with_more_bytes_than_declared_is_400_and_stores_nothing(client: Client) -> None:
    response = client.put(put_url(size=5), data=PDF, content_type="application/pdf")

    assert response.status_code == 400
    assert get_storage().head("uploads/abc") is None


def test_put_after_expiry_is_403(client: Client) -> None:
    response = client.put(put_url(minutes=-1), data=PDF, content_type="application/pdf")

    assert response.status_code == 403


def test_get_is_405(client: Client) -> None:
    assert client.get(put_url()).status_code == 405


def test_copy_and_delete(client: Client) -> None:
    client.put(put_url(), data=PDF, content_type="application/pdf")
    storage = get_storage()

    storage.copy("uploads/abc", "files/xyz")
    storage.delete("uploads/abc")

    assert storage.head("files/xyz") == StoredObject(len(PDF), "application/pdf")
    assert storage.head("uploads/abc") is None


def test_copy_overwrites_the_target(client: Client) -> None:
    storage = get_storage()
    client.put(put_url("uploads/one", size=3), data=b"old", content_type="application/pdf")
    client.put(put_url("uploads/two", size=7), data=b"new new", content_type="application/pdf")

    storage.copy("uploads/one", "files/xyz")
    storage.copy("uploads/two", "files/xyz")

    assert storage.head("files/xyz") == StoredObject(7, "application/pdf")


def test_delete_of_missing_key_is_fine() -> None:
    get_storage().delete("uploads/nope")


@pytest.mark.parametrize("key", ["../secret", "uploads/../../x"])
def test_keys_cannot_leave_the_root(key: str) -> None:
    with pytest.raises(ValueError, match="key"):
        get_storage().head(key)
