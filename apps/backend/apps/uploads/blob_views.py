"""The PUT and GET endpoints of the local stand-in for Vercel Blob.

Protected by the signed token in the URL, not by the session, like a real
storage URL. PUT streams the body to disk and refuses anything that differs
from what the token declared; GET streams the bytes back as an attachment.
"""

from datetime import datetime
from typing import Any

from django.core import signing
from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse
from django.http.response import HttpResponseBase
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .storage import GET_TOKEN_SALT, PUT_TOKEN_SALT, LocalBlobStorage

CHUNK = 64 * 1024


@csrf_exempt
@require_http_methods(["GET", "PUT"])
def blob(request: HttpRequest, key: str) -> HttpResponseBase:
    if request.method == "GET":
        return get_blob(request, key)
    return put_blob(request, key)


def claims_for(request: HttpRequest, key: str, salt: str) -> dict[str, Any] | None:
    """The token's claims if it was signed with salt for this key and is still valid."""
    try:
        claims: dict[str, Any] = signing.loads(request.GET.get("token", ""), salt=salt)
    except signing.BadSignature:
        return None
    if claims["key"] != key or datetime.fromisoformat(claims["expires_at"]) <= timezone.now():
        return None
    return claims


def get_blob(request: HttpRequest, key: str) -> HttpResponseBase:
    claims = claims_for(request, key, GET_TOKEN_SALT)
    if claims is None:
        return JsonResponse({"error": "bad token"}, status=403)
    storage = LocalBlobStorage()
    path = storage.path_for(key)
    if not path.is_file():
        return JsonResponse({"error": "not found"}, status=404)
    return FileResponse(
        path.open("rb"),
        as_attachment=True,
        filename=claims["filename"],
        content_type=storage.mime_path(path).read_text(),
    )


def put_blob(request: HttpRequest, key: str) -> HttpResponse:
    claims = claims_for(request, key, PUT_TOKEN_SALT)
    if claims is None:
        return JsonResponse({"error": "bad token"}, status=403)
    if request.content_type != claims["mime_type"]:
        return JsonResponse({"error": "content-type differs from the declared type"}, status=400)

    storage = LocalBlobStorage()
    path = storage.path_for(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    received = 0
    with partial.open("wb") as out:
        while chunk := request.read(CHUNK):
            received += len(chunk)
            if received > claims["size_bytes"]:
                break
            out.write(chunk)
    if received > claims["size_bytes"]:
        partial.unlink()
        return JsonResponse({"error": "body is larger than the declared size"}, status=400)

    partial.replace(path)
    storage.mime_path(path).write_text(claims["mime_type"])
    return JsonResponse({})
