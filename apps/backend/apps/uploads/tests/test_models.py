from datetime import timedelta

import pytest
from django.utils import timezone

from apps.sharing.tests.helpers import make_file, make_user
from apps.uploads.models import UPLOAD_TTL, Upload, to_json


@pytest.mark.django_db
def test_start_reserves_a_new_file_for_15_minutes() -> None:
    before = timezone.now()

    upload = Upload.start(make_user(), "Q1 Budget.xlsx", "application/vnd.ms-excel", 201734)

    assert timedelta(minutes=15) == UPLOAD_TTL
    assert before + UPLOAD_TTL <= upload.expires_at <= timezone.now() + UPLOAD_TTL
    assert upload.file is None
    assert not upload.is_replace
    assert not upload.is_done
    assert not upload.is_expired
    assert upload.storage_key == f"uploads/{upload.id}"


@pytest.mark.django_db
def test_start_for_a_file_is_a_replace() -> None:
    user = make_user()
    budget = make_file(user, "Q4 Budget.xls")

    upload = Upload.start(user, budget.name, "application/vnd.ms-excel", 10, file=budget)

    assert upload.is_replace
    assert upload.file == budget


@pytest.mark.django_db
def test_upload_is_expired_after_expires_at() -> None:
    upload = Upload.start(make_user(), "a.pdf", "application/pdf", 1)
    upload.expires_at = timezone.now() - timedelta(seconds=1)

    assert upload.is_expired


@pytest.mark.django_db
def test_to_json_has_the_spec_shape() -> None:
    upload = Upload.start(make_user(), "a.pdf", "application/pdf", 1)

    assert to_json(upload, "https://example.test/put") == {
        "id": str(upload.id),
        "name": "a.pdf",
        "put_url": "https://example.test/put",
        "put_headers": {"content-type": "application/pdf"},
        "expires_at": upload.expires_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
