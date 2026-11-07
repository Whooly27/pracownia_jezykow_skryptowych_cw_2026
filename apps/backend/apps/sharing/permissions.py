"""The six file permissions from the spec's access model."""

from collections.abc import Iterable
from enum import StrEnum

from django.core.exceptions import ValidationError


class Permission(StrEnum):
    VIEW = "view"
    EDIT = "edit"
    RENAME = "rename"
    DELETE = "delete"
    SHARE = "share"
    LINK = "link"   # owner tworzenie linkow


ALL_PERMISSIONS: tuple[str, ...] = tuple(p.value for p in Permission)

FOLDER_OWNER_PERMISSIONS: frozenset[str] = frozenset(
    {Permission.VIEW, Permission.RENAME, Permission.DELETE}
)


def validate_permissions(permissions: Iterable[str]) -> None:
    """A permission set is a list of known names, without repeats, that includes view."""
    values = list(permissions)
    unknown = [p for p in values if p not in ALL_PERMISSIONS]
    if unknown:
        raise ValidationError(f"unknown permission: {', '.join(unknown)}", code="validation_failed")
    if len(set(values)) != len(values):
        raise ValidationError("A permission is listed twice.", code="validation_failed")
    if Permission.VIEW not in values:
        raise ValidationError("Every permission set includes view.", code="validation_failed")
