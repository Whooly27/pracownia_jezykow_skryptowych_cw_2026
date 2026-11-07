import json
from datetime import UTC, datetime

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory

from apps.accounts.models import User
from apps.core.api import ApiError, api_get, api_view, iso, json_body, no_content, not_found, ok


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


@api_get
def listing(request: HttpRequest) -> HttpResponse:
    return ok([])


@api_view
def many_problems(request: HttpRequest) -> HttpResponse:
    raise ApiError(422, "validation_failed", messages=["a is bad", "b is bad"])


@pytest.mark.django_db
def test_api_get_rejects_post() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")

    assert listing(post(user)).status_code == 405


def test_api_get_anonymous_is_401() -> None:
    request = RequestFactory().get("/x")
    request.user = AnonymousUser()

    assert listing(request).status_code == 401


@pytest.mark.django_db
def test_api_error_with_several_messages_lists_one_error_each() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")

    response = many_problems(post(user))

    assert response.status_code == 422
    assert json.loads(response.content)["errors"] == [
        {"code": "validation_failed", "message": "a is bad"},
        {"code": "validation_failed", "message": "b is bad"},
    ]


def test_not_found_names_the_file() -> None:
    error = not_found("b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40")

    assert (error.status, error.code) == (404, "not_found")
    assert (
        error.message
        == "File b5d8e3a1-0f7c-4c29-9e6b-3a2d8f1c7e40 doesn't exist or you can't see it."
    )


def test_no_content_has_204_and_empty_body() -> None:
    response = no_content()

    assert response.status_code == 204
    assert response.content == b""
