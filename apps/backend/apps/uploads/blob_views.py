"""The PUT endpoint of the local stand-in for Vercel Blob.

Protected by the signed token in the URL, not by the session, like a real
storage URL. Streams the body to disk and refuses anything that differs
from what the token declared.
"""

from datetime import datetime

from django.core import signing
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .storage import PUT_TOKEN_SALT, LocalBlobStorage

CHUNK = 64 * 1024


@csrf_exempt
@require_http_methods(["PUT"])
def put_blob(request: HttpRequest, key: str) -> HttpResponse:
    try:
        claims = signing.loads(request.GET.get("token", ""), salt=PUT_TOKEN_SALT)
    except signing.BadSignature:
        return JsonResponse({"error": "bad token"}, status=403)
    if claims["key"] != key or datetime.fromisoformat(claims["expires_at"]) <= timezone.now():
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
