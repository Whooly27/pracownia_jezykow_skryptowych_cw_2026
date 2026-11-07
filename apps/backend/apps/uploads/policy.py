"""What may be uploaded: allowed types and the size limit, from the spec."""

from dataclasses import dataclass
from typing import Any, NoReturn

from apps.core.api import ApiError
from apps.files.models import NAME_MAX_LENGTH

MAX_FILE_BYTES = 25 * 1024 * 1024

MIME_BY_EXTENSION: dict[str, str] = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "ppt": "application/vnd.ms-powerpoint",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "odt": "application/vnd.oasis.opendocument.text",
    "ods": "application/vnd.oasis.opendocument.spreadsheet",
    "odp": "application/vnd.oasis.opendocument.presentation",
    "rtf": "application/rtf",
    "txt": "text/plain",
    "csv": "text/csv",
    "md": "text/markdown",
}


@dataclass(frozen=True)
class Rejection:
    code: str
    message: str


STATUS_BY_CODE = {
    "validation_failed": 422,
    "unsupported_file_type": 415,
    "file_too_large": 413,
    "name_conflict": 409,
}


def raise_for(rejection: Rejection) -> NoReturn:
    raise ApiError(STATUS_BY_CODE[rejection.code], rejection.code, rejection.message)


def upload_policy() -> dict[str, Any]:
    return {"max_file_bytes": MAX_FILE_BYTES, "allowed_extensions": list(MIME_BY_EXTENSION)}


def extension_of(name: str) -> str:
    _, dot, extension = name.rpartition(".")
    return extension.lower() if dot else ""


def name_problems(name: str) -> list[str]:
    """Every rule the name breaks, so a 422 can list them all."""
    problems: list[str] = []
    if not name.strip():
        problems.append("Name can't be empty.")
    if len(name) > NAME_MAX_LENGTH:
        problems.append("Name is over 255 characters.")
    if "/" in name:
        problems.append("Name can't contain /.")
    return problems


def check_name(name: str) -> Rejection | None:
    problems = name_problems(name)
    return Rejection("validation_failed", problems[0]) if problems else None


def check_type(name: str, mime_type: str) -> Rejection | None:
    extension = extension_of(name)
    expected = MIME_BY_EXTENSION.get(extension)
    if expected is None:
        return Rejection(
            "unsupported_file_type",
            f"{name}: files of type .{extension} can't be uploaded."
            if extension
            else f"{name}: files without an extension can't be uploaded.",
        )
    if mime_type != expected:
        return Rejection("unsupported_file_type", f"{name}: type doesn't match .{extension}.")
    return None


def check_size(size_bytes: object) -> Rejection | None:
    if isinstance(size_bytes, bool) or not isinstance(size_bytes, int) or size_bytes < 1:
        return Rejection("validation_failed", "size_bytes must be a positive whole number.")
    if size_bytes > MAX_FILE_BYTES:
        return Rejection("file_too_large", "Files over 25 MB can't be uploaded.")
    return None


def check_new_file(name: str, size_bytes: object, mime_type: str) -> Rejection | None:
    return check_name(name) or check_type(name, mime_type) or check_size(size_bytes)
