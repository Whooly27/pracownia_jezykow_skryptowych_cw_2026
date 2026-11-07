"""File endpoints: list, rename, delete, remove access, download."""

import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from apps.core.api import (
    ApiError,
    api_get,
    api_view,
    iso,
    json_body,
    no_content,
    not_found,
    ok,
    signed_in_user,
)
from apps.sharing.access import access_for
from apps.sharing.models import Grant
from apps.uploads.models import Upload
from apps.uploads.policy import check_type, name_problems, raise_for, upload_policy
from apps.uploads.storage import get_storage

from .listing import page, parse_query
from .models import File
from .serializers import file_to_json

DOWNLOAD_TTL = timedelta(seconds=60)


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
    if Upload.pending(user).filter(name=name).exists():
        raise conflict
    try:
        file.full_clean()
    except ValidationError as error:
        raise conflict from error
    try:
        file.save()
    except IntegrityError as error:
        raise conflict from error
    return ok(file_to_json(file, user))


@api_view
def delete_file(request: HttpRequest, file_id: uuid.UUID) -> HttpResponse:
    user = signed_in_user(request)
    file = File.objects.filter(id=file_id).first()
    access = access_for(user, file) if file is not None else None
    if file is None or access is None:
        raise not_found(file_id)
    if "delete" not in access.permissions:
        raise ApiError(403, "forbidden", "You don't have delete on this file.")
    key = file.storage_key  # delete() clears the id, so read the key first
    file.delete()
    get_storage().delete(key)
    return no_content()


@api_view
def remove_access(request: HttpRequest, file_id: uuid.UUID) -> HttpResponse:
    user = signed_in_user(request)
    grants = Grant.objects.filter(file_id=file_id, user=user)
    if not grants.exists():
        raise ApiError(404, "not_found", "The file isn't shared with you.")
    grants.delete()
    return no_content()


@api_view
def download_file(request: HttpRequest, file_id: uuid.UUID) -> HttpResponse:
    user = signed_in_user(request)
    file = File.objects.filter(id=file_id).first()
    if file is None or access_for(user, file) is None:
        raise not_found(file_id)
    expires_at = timezone.now() + DOWNLOAD_TTL
    url = get_storage().get_url(file.storage_key, file.name, expires_at)
    return ok({"url": url, "expires_at": iso(expires_at)})
