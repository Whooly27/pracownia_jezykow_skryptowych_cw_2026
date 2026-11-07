"""File endpoints: list, rename, delete, remove access, download."""

from django.http import HttpRequest, HttpResponse

from apps.core.api import api_get, ok, signed_in_user
from apps.uploads.policy import upload_policy

from .listing import page, parse_query
from .serializers import file_to_json


@api_get
def list_files(request: HttpRequest) -> HttpResponse:
    user = signed_in_user(request)
    query = parse_query(request.GET)
    items, has_more = page(user, query)
    return ok(
        {
            "upload_policy": upload_policy() if query.scope == "mine" else None,
            "items": [file_to_json(file, user) for file in items],
            "has_more": has_more,
        }
    )
