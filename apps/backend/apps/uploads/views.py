"""Upload endpoints: reserve a name, then make the file visible once the bytes arrived."""

from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from apps.core.api import ApiError, api_view, json_body, ok, signed_in_user
from apps.files.models import File
from apps.files.serializers import file_to_json
from apps.sharing.access import access_for

from .models import Upload, to_json
from .policy import check_size, check_type, name_problems, raise_for
from .storage import StoredObject, get_storage


@api_view
def start_upload(request: HttpRequest) -> HttpResponse:
    user = signed_in_user(request)
    body = json_body(request)
    name = str(body.get("name", "")).strip()
    mime_type = str(body.get("mime_type", ""))
    problems = name_problems(name)
    if problems:
        raise ApiError(422, "validation_failed", messages=problems)
    rejection = check_type(name, mime_type) or check_size(body.get("size_bytes"))
    if rejection is not None:
        raise_for(rejection)
    if File.objects.filter(owner=user, name=name).exists():
        raise ApiError(409, "name_conflict", f"{name}: you already have a file with that name.")

    storage = get_storage()
    # Starting the same name again replaces your own pending upload.
    for old in Upload.objects.filter(owner=user, name=name, is_replace=False):
        if not old.is_done:
            storage.delete(old.storage_key)
            old.delete()
    upload = Upload.start(user, name, mime_type, body["size_bytes"])
    put_url = storage.put_url(
        upload.storage_key, upload.mime_type, upload.size_bytes, upload.expires_at
    )
    return ok(to_json(upload, put_url), 201)


@api_view
def replace_file(request: HttpRequest, file_id: UUID) -> HttpResponse:
    user = signed_in_user(request)
    file = File.objects.filter(id=file_id).first()
    _require_edit(user, file)
    assert file is not None  # noqa: S101  (narrowed by _require_edit)
    body = json_body(request)
    mime_type = str(body.get("mime_type", ""))
    rejection = check_size(body.get("size_bytes")) or check_type(file.name, mime_type)
    if rejection is not None:
        raise_for(rejection)

    upload = Upload.start(user, file.name, mime_type, body["size_bytes"], file=file)
    put_url = get_storage().put_url(
        upload.storage_key, upload.mime_type, upload.size_bytes, upload.expires_at
    )
    return ok(to_json(upload, put_url), 201)


@api_view
def complete_upload(request: HttpRequest, upload_id: UUID) -> HttpResponse:
    user = signed_in_user(request)
    upload = Upload.objects.select_related("file").filter(id=upload_id, owner=user).first()
    if upload is None:
        raise ApiError(404, "not_found", "No such upload.")
    if upload.is_replace:
        _require_edit(user, upload.file)
    if upload.is_done and upload.file is not None:
        return ok(file_to_json(upload.file, user))
    if upload.is_expired:
        raise ApiError(410, "upload_expired", "The upload wasn't finished within 15 minutes.")

    storage = get_storage()
    expected = StoredObject(upload.size_bytes, upload.mime_type)
    if storage.head(upload.storage_key) != expected:
        raise ApiError(409, "upload_incomplete", "The bytes haven't arrived yet.")

    now = timezone.now()
    with transaction.atomic():
        if upload.file is None:
            file = File(
                owner=user,
                name=upload.name,
                mime_type=upload.mime_type,
                size_bytes=upload.size_bytes,
                modified_at=now,
            )
            _save_new_file(file)
        else:
            file = upload.file
            file.mime_type = upload.mime_type
            file.size_bytes = upload.size_bytes
            file.modified_at = now
            file.save(update_fields=["mime_type", "size_bytes", "modified_at"])
        storage.copy(upload.storage_key, file.storage_key)
        upload.file = file
        upload.completed_at = now
        upload.save(update_fields=["file", "completed_at"])
    storage.delete(upload.storage_key)
    return ok(file_to_json(file, user))


def _require_edit(user: Any, file: File | None) -> None:
    access = access_for(user, file) if file is not None else None
    if access is None:
        raise ApiError(404, "not_found", "The file doesn't exist or you can't see it.")
    if "edit" not in access.permissions:
        raise ApiError(403, "forbidden", "You don't have edit on this file.")


def _save_new_file(file: File) -> None:
    conflict = ApiError(
        409, "name_conflict", f"{file.name}: you already have a file with that name."
    )
    try:
        file.full_clean()
    except ValidationError as e:
        raise conflict from e
    try:
        file.save()
    except IntegrityError as e:
        raise conflict from e
