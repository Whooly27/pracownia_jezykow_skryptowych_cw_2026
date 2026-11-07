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
    response = post_json(client, "/api/v1/uploads", PDF)

    assert response.status_code == 401
    assert response.json()["errors"][0]["code"] == "unauthenticated"


@pytest.mark.django_db
def test_start_returns_one_upload(client: Client) -> None:
    response = start_upload(client, make_user(), XLSX)

    assert response.status_code == 201
    upload = response.json()["data"]
    assert upload["name"] == "Q1 Budget.xlsx"
    assert upload["put_headers"] == {"content-type": XLSX_MIME}
    assert upload["put_url"] == get_storage().put_url(
        f"uploads/{upload['id']}",
        XLSX_MIME,
        201734,
        Upload.objects.get(id=upload["id"]).expires_at,
    )


@pytest.mark.django_db
def test_name_taken_is_409(client: Client) -> None:
    user = make_user()
    make_file(user, "Brand brief v2.pdf")

    response = start_upload(client, user, PDF)

    assert response.status_code == 409
    assert response.json() == {
        "data": None,
        "errors": [
            {
                "code": "name_conflict",
                "message": "Brand brief v2.pdf: you already have a file with that name.",
            }
        ],
    }


@pytest.mark.django_db
def test_exe_is_415(client: Client) -> None:
    exe = {"name": "setup.exe", "size_bytes": 10, "mime_type": "application/octet-stream"}

    response = start_upload(client, make_user(), exe)

    assert response.status_code == 415
    assert response.json()["errors"][0]["code"] == "unsupported_file_type"


@pytest.mark.django_db
def test_over_25mb_is_413(client: Client) -> None:
    huge = {**PDF, "size_bytes": 26214401}

    response = start_upload(client, make_user(), huge)

    assert response.status_code == 413
    assert response.json()["errors"][0]["code"] == "file_too_large"


@pytest.mark.django_db
def test_bad_name_lists_every_problem_422(client: Client) -> None:
    bad = {**PDF, "name": "x" * 256 + "/y.pdf"}

    response = start_upload(client, make_user(), bad)

    assert response.status_code == 422
    assert [e["code"] for e in response.json()["errors"]] == ["validation_failed"] * 2


@pytest.mark.django_db
def test_bad_size_is_422(client: Client) -> None:
    response = start_upload(client, make_user(), {**PDF, "size_bytes": "big"})

    assert response.status_code == 422


@pytest.mark.django_db
def test_malformed_body_is_422(client: Client) -> None:
    client.force_login(make_user())

    response = client.post("/api/v1/uploads", data=b"[1,2]", content_type="application/json")

    assert response.status_code == 422


@pytest.mark.django_db
def test_restarting_a_pending_name_replaces_the_old_upload(client: Client) -> None:
    user = make_user()
    first = start_upload(client, user, PDF).json()["data"]
    client.put(first["put_url"], data=b"x", content_type="application/pdf")

    second = start_upload(client, user, PDF).json()["data"]

    assert second["id"] != first["id"]
    assert not Upload.objects.filter(id=first["id"]).exists()
    assert get_storage().head(f"uploads/{first['id']}") is None
