import pytest
from django.test import Client

from apps.sharing.tests.helpers import make_file, make_user
from apps.uploads.models import Upload
from apps.uploads.storage import get_storage

from .helpers import PDF, post_json, start_upload

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
XLSX = {"name": "Q1 Budget.xlsx", "size_bytes": 201734, "mime_type": XLSX_MIME}


@pytest.mark.django_db
def test_anonymous_is_401(client: Client) -> None:
    response = post_json(client, "/api/v1/uploads", {"files": [PDF]})

    assert response.status_code == 401
    assert response.json()["errors"][0]["code"] == "unauthenticated"


@pytest.mark.django_db
def test_mixed_request_returns_uploads_and_errors(client: Client) -> None:
    exe = {"name": "setup.exe", "size_bytes": 10, "mime_type": "application/octet-stream"}
    huge = {"name": "big.pdf", "size_bytes": 30 * 1024 * 1024, "mime_type": "application/pdf"}

    response = start_upload(client, make_user(), XLSX, exe, PDF, huge)

    assert response.status_code == 201
    body = response.json()
    assert [u["name"] for u in body["data"]] == ["Q1 Budget.xlsx", "Brand brief v2.pdf"]
    assert [e["code"] for e in body["errors"]] == ["unsupported_file_type", "file_too_large"]
    assert body["errors"][0]["message"].startswith("setup.exe")
    upload = body["data"][0]
    assert upload["put_url"] == get_storage().put_url(
        f"uploads/{upload['id']}",
        XLSX_MIME,
        201734,
        Upload.objects.get(id=upload["id"]).expires_at,
    )
    assert upload["put_headers"] == {"content-type": XLSX_MIME}


@pytest.mark.django_db
def test_name_taken_by_a_file_is_name_conflict(client: Client) -> None:
    user = make_user()
    make_file(user, "Brand brief v2.pdf")

    response = start_upload(client, user, PDF)

    assert response.json() == {
        "data": [],
        "errors": [
            {
                "code": "name_conflict",
                "message": "Brand brief v2.pdf: you already have a file with that name.",
            }
        ],
    }


@pytest.mark.django_db
def test_same_name_twice_in_one_request_rejects_the_second(client: Client) -> None:
    response = start_upload(client, make_user(), PDF, PDF)

    body = response.json()
    assert len(body["data"]) == 1
    assert body["errors"][0]["code"] == "name_conflict"


@pytest.mark.django_db
def test_restarting_a_pending_name_replaces_the_old_upload(client: Client) -> None:
    user = make_user()
    first = start_upload(client, user, PDF).json()["data"][0]
    client.put(first["put_url"], data=b"x", content_type="application/pdf")

    second = start_upload(client, user, PDF).json()["data"][0]

    assert second["id"] != first["id"]
    assert not Upload.objects.filter(id=first["id"]).exists()
    assert get_storage().head(f"uploads/{first['id']}") is None


@pytest.mark.django_db
def test_other_name_does_not_touch_pending_uploads(client: Client) -> None:
    user = make_user()
    first = start_upload(client, user, PDF).json()["data"][0]

    start_upload(client, user, XLSX)

    assert Upload.objects.filter(id=first["id"]).exists()


@pytest.mark.django_db
def test_empty_files_is_422(client: Client) -> None:
    response = start_upload(client, make_user())

    assert response.status_code == 422
    assert response.json()["errors"][0]["code"] == "validation_failed"


@pytest.mark.django_db
def test_101_files_is_422(client: Client) -> None:
    files = [{**PDF, "name": f"{i}.pdf"} for i in range(101)]

    assert start_upload(client, make_user(), *files).status_code == 422


@pytest.mark.django_db
def test_malformed_item_is_rejected_per_file(client: Client) -> None:
    response = start_upload(client, make_user(), {"name": "a.pdf"}, {"size_bytes": 1})

    assert response.status_code == 201
    assert [e["code"] for e in response.json()["errors"]] == [
        "unsupported_file_type",
        "validation_failed",
    ]


@pytest.mark.django_db
def test_files_not_a_list_is_422(client: Client) -> None:
    client.force_login(make_user())

    assert post_json(client, "/api/v1/uploads", {"files": "a.pdf"}).status_code == 422
