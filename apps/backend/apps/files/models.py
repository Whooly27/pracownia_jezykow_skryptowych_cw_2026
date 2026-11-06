"""Files and folders.

One table holds both kinds: they share a name, a parent, an owner and a path,
and a name must be unique among siblings regardless of kind.
"""

import uuid
from collections.abc import Collection
from typing import ClassVar

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.db.models import Q

NAME_MAX_LENGTH = 255


class Node(models.Model):
    class Kind(models.TextChoices):
        FILE = "file", "File"
        FOLDER = "folder", "Folder"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=6, choices=Kind.choices)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_nodes"
    )

    # File-only fields; null for folders.
    # Null, not "", for folders: the API returns null and the check constraint relies on it.
    mime_type = models.CharField(max_length=255, null=True, blank=True)  # noqa: DJ001
    size_bytes = models.BigIntegerField(null=True, blank=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["owner", "parent", "name"],
                nulls_distinct=False,
                name="node_name_unique_among_siblings",
                violation_error_code="name_conflict",
                violation_error_message="That name is already taken in this folder.",
            ),
            models.CheckConstraint(
                condition=~Q(name="") & ~Q(name__contains="/"),
                name="node_name_not_empty_no_slash",
            ),
            models.CheckConstraint(
                condition=Q(kind="file")
                | (
                    Q(mime_type__isnull=True)
                    & Q(size_bytes__isnull=True)
                    & Q(modified_at__isnull=True)
                    & Q(modified_by__isnull=True)
                ),
                name="node_folder_has_no_file_fields",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def is_folder(self) -> bool:
        return self.kind == self.Kind.FOLDER

    @property
    def is_file(self) -> bool:
        return self.kind == self.Kind.FILE

    def path(self) -> list["Node"]:
        """Ancestors, top level first; [] at the top level.

        Stops if the chain loops back, so an invalid parent (checked in clean)
        can't send this into an infinite loop.
        """
        ancestors: list[Node] = []
        seen = {self.id}
        current = self.parent
        while current is not None and current.id not in seen:
            seen.add(current.id)
            ancestors.append(current)
            current = current.parent
        ancestors.reverse()
        return ancestors

    def clean(self) -> None:
        errors: dict[str, list[str]] = {}

        self.name = self.name.strip()
        if not self.name:
            errors.setdefault("name", []).append("Name can't be empty.")
        if "/" in self.name:
            errors.setdefault("name", []).append("Name can't contain /.")

        if self.is_folder:
            for field in ("mime_type", "size_bytes", "modified_at", "modified_by"):
                if getattr(self, field) is not None:
                    errors.setdefault(field, []).append("A folder can't have this field set.")
        else:
            if self.mime_type is None:
                errors.setdefault("mime_type", []).append("A file needs a MIME type.")
            if self.size_bytes is None:
                errors.setdefault("size_bytes", []).append("A file needs a size.")

        if self.parent is not None:
            if not self.parent.is_folder:
                errors.setdefault("parent", []).append("The parent must be a folder.")
            if self.parent.owner_id != self.owner_id:
                errors.setdefault("parent", []).append("The parent must have the same owner.")
            chain = [self.parent, *self.parent.path()]
            if any(node.id == self.id for node in chain):
                errors.setdefault("parent", []).append("A folder can't be moved under itself.")

        if errors:
            raise ValidationError(errors)

    def validate_constraints(self, exclude: Collection[str] | None = None) -> None:
        # Django reports a unique-constraint clash as a non-field error; callers
        # want it on "name", the field the user typed.
        try:
            super().validate_constraints(exclude)
        except ValidationError as e:
            conflicts = [
                err for err in e.error_dict.get(NON_FIELD_ERRORS, []) if err.code == "name_conflict"
            ]
            if conflicts:
                raise ValidationError({"name": conflicts}) from e
            raise
