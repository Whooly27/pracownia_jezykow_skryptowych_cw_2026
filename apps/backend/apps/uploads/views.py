"""Upload endpoints: reserve a name, then make the file visible once the bytes arrived."""

from typing import Any

from django.http import HttpRequest, HttpResponse

from apps.core.api import ApiError, api_view, json_body, ok, signed_in_user
from apps.files.models import File

from .models import Upload, to_json
from .policy import Rejection, check_new_file
from .storage import get_storage

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
