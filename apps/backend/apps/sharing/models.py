"""Sharing: the owner creates links, people who open a link get a grant.

Links are the only way to get access. A grant records who joined through
which link and holds a copy of that link's permissions. Deleting a link
deletes its grants, so a grant exists only while it gives access.
"""

import uuid
from typing import ClassVar

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.files.models import File

from .permissions import validate_permissions


def permissions_field() -> "ArrayField[list[str], list[str]]":
    return ArrayField(models.CharField(max_length=6), default=list)


class ShareLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="links")
    # Only a hash of the token is stored; the URL is shown once, at creation.
    token_hash = models.CharField(max_length=64, unique=True)
    permissions = permissions_field()
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_links"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # Set when the owner deletes the link, so redeem can answer "link_deleted".
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self) -> str:
        return f"Link to {self.file} by {self.created_by}"

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and self.expires_at <= timezone.now()

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def redemption_count(self) -> int:
        return self.grants.count()

    def clean(self) -> None:
        validate_permissions(self.permissions)


class Grant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="grants")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grants"
    )
    link = models.ForeignKey(ShareLink, on_delete=models.CASCADE, related_name="grants")
    permissions = permissions_field()
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["granted_at"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(fields=["user", "link"], name="grant_unique_per_user_and_link"),
        ]

    def __str__(self) -> str:
        return f"{self.user} on {self.file}: {', '.join(self.permissions)}"

    def clean(self) -> None:
        validate_permissions(self.permissions)
        errors: dict[str, list[str]] = {}
        if self.file_id is not None and self.user_id == self.file.owner_id:
            errors["user"] = ["The owner already holds every permission."]
        if self.link_id is not None and list(self.permissions) != list(self.link.permissions):
            errors["permissions"] = ["A grant holds exactly what its link gives."]
        if errors:
            raise ValidationError(errors)
