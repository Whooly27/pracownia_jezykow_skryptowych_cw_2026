"""The small set of helpers every API view uses.

Responses always have the shape ``{"data": ..., "errors": [...]}``. A view
raises ``ApiError`` for a whole-request failure and ``api_view`` turns it
into that envelope.
"""

import functools
import json
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.accounts.models import User


class ApiError(Exception):
    """A failed request. One message, or several for a 422 that lists every problem."""

    def __init__(
        self, status: int, code: str, message: str = "", messages: Sequence[str] = ()
    ) -> None:
        super().__init__(message or "; ".join(messages))
        self.status = status
        self.code = code
        self.message = message
        self.messages = list(messages)


def ok(data: Any, status: int = 200, errors: Sequence[dict[str, str]] = ()) -> JsonResponse:
    return JsonResponse({"data": data, "errors": list(errors)}, status=status)


def fail(status: int, code: str, message: str = "", messages: Sequence[str] = ()) -> JsonResponse:
    errors = [{"code": code, "message": m} for m in (messages or [message])]
    return JsonResponse({"data": None, "errors": errors}, status=status)


def no_content() -> HttpResponse:
    return HttpResponse(status=204)


def not_found(file_id: object) -> ApiError:
    return ApiError(404, "not_found", f"File {file_id} doesn't exist or you can't see it.")


def _api(
    methods: list[str],
) -> Callable[[Callable[..., HttpResponse]], Callable[..., HttpResponse]]:
    def decorator(view: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        @functools.wraps(view)
        def wrapped(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            if not request.user.is_authenticated:
                return fail(401, "unauthenticated", "No valid session.")
            try:
                return view(request, *args, **kwargs)
            except ApiError as e:
                return fail(e.status, e.code, e.message, e.messages)

        return csrf_exempt(require_http_methods(methods)(wrapped))

    return decorator


# Signed-in users only, ApiError turned into the envelope. API views are exempt from
# CSRF for now: the session cookie is SameSite=Lax, which already blocks a POST from
# another site. Revisit with Cognito.
api_view = _api(["POST"])
api_get = _api(["GET"])


def signed_in_user(request: HttpRequest) -> User:
    """The request's user as a User; api_view already turned anyone else away."""
    user = request.user
    if not isinstance(user, User):
        raise ApiError(401, "unauthenticated", "No valid session.")
    return user


def json_body(request: HttpRequest) -> dict[str, Any]:
    try:
        body = json.loads(request.body)
    except ValueError:
        body = None
    if not isinstance(body, dict):
        raise ApiError(422, "validation_failed", "Malformed body.")
    return body


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
