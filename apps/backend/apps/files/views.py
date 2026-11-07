"""File endpoints: list, rename, delete, remove access, download."""

import uuid

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from apps.core.api import ApiError, api_get, api_view, json_body, not_found, ok, signed_in_user
from apps.sharing.access import access_for
from apps.uploads.policy import check_type, name_problems, raise_for, upload_policy

from .listing import page, parse_query
from .models import File
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


@api_view
def rename_file(request: HttpRequest, file_id: uuid.UUID) -> HttpResponse:
    user = signed_in_user(request)
    file = File.objects.filter(id=file_id).first()
    if file is None or access_for(user, file) is None:
        raise not_found(file_id)
    if file.owner_id != user.id:
        raise ApiError(403, "forbidden", "Only the owner can rename a file.")
    name = str(json_body(request).get("name", "")).strip()
    problems = name_problems(name)
    if problems:
        raise ApiError(422, "validation_failed", messages=problems)
    rejection = check_type(name, file.mime_type)
    if rejection:
        raise_for(rejection)
    file.name = name
    file.modified_at = timezone.now()
    conflict = ApiError(409, "name_conflict", f"{name}: you already have a file with that name.")
    try:
        file.full_clean()
    except ValidationError as error:
        raise conflict from error
    try:
        file.save()
    except IntegrityError as error:
        raise conflict from error
    return ok(file_to_json(file, user))
