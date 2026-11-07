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
from .policy import Rejection, check_new_file, check_size, check_type
from .storage import StoredObject, get_storage

MAX_FILES_PER_REQUEST = 100


@api_view
def start_upload(request: HttpRequest) -> HttpResponse:
    files = json_body(request).get("files")
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES_PER_REQUEST:
        raise ApiError(422, "validation_failed", "files must hold 1 to 100 entries.")

    user = signed_in_user(request)
    storage = get_storage()
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    taken: set[str] = set()
    for item in files:
        name, rejection = _check_item(item, user.id, taken)
        if rejection is not None:
            rejected.append({"code": rejection.code, "message": rejection.message})
            continue
        taken.add(name)
        # Starting the same name again replaces your own pending upload.
        for old in Upload.objects.filter(owner=user, name=name, is_replace=False):
            if not old.is_done:
                storage.delete(old.storage_key)
                old.delete()
        upload = Upload.start(user, name, item["mime_type"], item["size_bytes"])
        put_url = storage.put_url(
            upload.storage_key, upload.mime_type, upload.size_bytes, upload.expires_at
        )
        accepted.append(to_json(upload, put_url))
    return ok(accepted, 201, errors=rejected)


def _check_item(item: Any, owner_id: Any, taken: set[str]) -> tuple[str, Rejection | None]:
    if not isinstance(item, dict):
        return "", Rejection("validation_failed", f"{item}: each entry must be an object.")
    name = str(item.get("name", "")).strip()
    rejection = check_new_file(name, item.get("size_bytes"), str(item.get("mime_type", "")))
    if rejection is None and (
        name in taken or File.objects.filter(owner_id=owner_id, name=name).exists()
    ):
        rejection = Rejection("name_conflict", f"{name}: you already have a file with that name.")
    return name, rejection


@api_view
def replace_file(request: HttpRequest, file_id: UUID) -> HttpResponse:
    user = signed_in_user(request)
    file = File.objects.filter(id=file_id).first()
    _require_edit(user, file)
    assert file is not None  # noqa: S101  (narrowed by _require_edit)
    body = json_body(request)
    mime_type = str(body.get("mime_type", ""))
    rejection = check_size(body.get("size_bytes"))
    if rejection is not None:
        status = 413 if rejection.code == "file_too_large" else 422
        raise ApiError(status, rejection.code, rejection.message)
    rejection = check_type(file.name, mime_type)
    if rejection is not None:
        raise ApiError(415, rejection.code, rejection.message)

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
