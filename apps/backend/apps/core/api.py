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
from django.views.decorators.http import require_POST


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str = "") -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def ok(data: Any, status: int = 200, errors: Sequence[dict[str, str]] = ()) -> JsonResponse:
    return JsonResponse({"data": data, "errors": list(errors)}, status=status)


def fail(status: int, code: str, message: str = "") -> JsonResponse:
    return JsonResponse(
        {"data": None, "errors": [{"code": code, "message": message}]}, status=status
    )


def api_view(view: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """POST only, signed-in users only, ApiError turned into the envelope.

    API views are exempt from CSRF for now: the session cookie is SameSite=Lax,
    which already blocks a POST from another site. Revisit with Cognito.
    """

    @functools.wraps(view)
    def wrapped(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return fail(401, "unauthenticated", "No valid session.")
        try:
            return view(request, *args, **kwargs)
        except ApiError as e:
            return fail(e.status, e.code, e.message)

    return csrf_exempt(require_POST(wrapped))


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
