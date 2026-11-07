import json
from datetime import UTC, datetime

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory

from apps.accounts.models import User
from apps.core.api import ApiError, api_view, iso, json_body, ok


@api_view
def echo(request: HttpRequest) -> HttpResponse:
    return ok({"hello": str(request.user)})


@api_view
def expired(request: HttpRequest) -> HttpResponse:
    raise ApiError(410, "upload_expired", "Start again.")


def post(user: User | AnonymousUser, body: bytes = b"{}") -> HttpRequest:
    request = RequestFactory().post("/x", data=body, content_type="application/json")
    request.user = user
    return request


def test_anonymous_gets_401() -> None:
    response = echo(post(AnonymousUser()))

    assert response.status_code == 401
    assert json.loads(response.content) == {
        "data": None,
        "errors": [{"code": "unauthenticated", "message": "No valid session."}],
    }


@pytest.mark.django_db
def test_signed_in_user_gets_the_envelope() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")

    response = echo(post(user))

    assert response.status_code == 200
    assert json.loads(response.content) == {"data": {"hello": "test_user"}, "errors": []}


@pytest.mark.django_db
def test_get_is_405() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    request = RequestFactory().get("/x")
    request.user = user

    assert echo(request).status_code == 405


@pytest.mark.django_db
def test_api_error_becomes_envelope() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")

    response = expired(post(user))

    assert response.status_code == 410
    assert json.loads(response.content) == {
        "data": None,
        "errors": [{"code": "upload_expired", "message": "Start again."}],
    }


@pytest.mark.parametrize("body", [b"{", b"[]", b"42", b""])
def test_json_body_rejects_anything_but_an_object(body: bytes) -> None:
    with pytest.raises(ApiError) as e:
        json_body(post(AnonymousUser(), body))

    assert (e.value.status, e.value.code) == (422, "validation_failed")


def test_json_body_returns_the_object() -> None:
    assert json_body(post(AnonymousUser(), b'{"a": 1}')) == {"a": 1}


def test_iso_formats_utc_without_microseconds() -> None:
    assert iso(datetime(2026, 11, 5, 10, 2, 0, 123456, tzinfo=UTC)) == "2026-11-05T10:02:00Z"
