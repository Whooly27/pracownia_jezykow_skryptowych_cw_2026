"""Sharing: grants give people permissions on one file, links hand out grants.

Only files are shared, never folders. Access to a folder on the path to a
shared file is derived (see access.py), not stored.
"""

import uuid
from typing import ClassVar

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.files.models import Node

from .permissions import validate_permissions


def permissions_field() -> "ArrayField[list[str], list[str]]":
    return ArrayField(models.CharField(max_length=6), default=list)


def _file_only(node: Node | None) -> None:
    if node is not None and not node.is_file:
        raise ValidationError({"file": ["Only files can be shared, never folders."]})


class ShareLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="links")
    # Only a hash of the token is stored; the URL is shown once, at creation.
    token_hash = models.CharField(max_length=64, unique=True)
    permissions = permissions_field()
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_links"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["created_at"]

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
        _file_only(self.file)
        validate_permissions(self.permissions)


class Grant(models.Model):
    class Via(models.TextChoices):
        DIRECT = "direct", "Invited directly"
        LINK = "link", "Joined through a link"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="grants")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grants"
    )
    permissions = permissions_field()
    via = models.CharField(max_length=6, choices=Via.choices, default=Via.DIRECT)
    link = models.ForeignKey(
        ShareLink, null=True, blank=True, on_delete=models.CASCADE, related_name="grants"
    )
    # Who gave the access: the inviter, or the link's creator. Decides who may
    # change or remove it later.
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="grants_given"
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["granted_at"]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            # One grant per (giver, receiver) directly, and one per link.
            models.UniqueConstraint(
                fields=["file", "user", "granted_by", "link"],
                nulls_distinct=False,
                name="grant_unique_per_giver_and_link",
            ),
            models.CheckConstraint(
                condition=(Q(via="direct") & Q(link__isnull=True))
                | (Q(via="link") & Q(link__isnull=False)),
                name="grant_link_matches_via",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} on {self.file}: {', '.join(self.permissions)}"

    def clean(self) -> None:
        _file_only(self.file)
        validate_permissions(self.permissions)
        errors: dict[str, list[str]] = {}
        if self.file_id is not None and self.user_id == self.file.owner_id:
            errors["user"] = ["The owner already holds every permission."]
        if self.via == self.Via.DIRECT and self.link_id is not None:
            errors["link"] = ["A direct grant doesn't come from a link."]
        if self.via == self.Via.LINK and self.link_id is None:
            errors["link"] = ["A link grant needs its link."]
        if errors:
            raise ValidationError(errors)
