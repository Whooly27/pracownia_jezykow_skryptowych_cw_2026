"""Files: one flat list per owner, no folders.

A file has exactly one owner and a name that is unique among that owner's
files. The bytes live in storage under ``storage_key``; this row holds only
what the API shows.
"""

import uuid
from collections.abc import Collection
from typing import ClassVar

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.db.models import Q

NAME_MAX_LENGTH = 255


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_files"
    )
    mime_type = models.CharField(max_length=255)
    size_bytes = models.BigIntegerField()
    modified_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="file_name_unique_per_owner",
                violation_error_code="name_conflict",
                violation_error_message="You already have a file with that name.",
            ),
            models.CheckConstraint(
                condition=~Q(name="") & ~Q(name__contains="/"),
                name="file_name_not_empty_no_slash",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def storage_key(self) -> str:
        return f"files/{self.id}"

    def clean(self) -> None:
        self.name = self.name.strip()
        errors: list[str] = []
        if not self.name:
            errors.append("Name can't be empty.")
        if "/" in self.name:
            errors.append("Name can't contain /.")
        if errors:
            raise ValidationError({"name": errors})

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
