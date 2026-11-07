"""An upload in progress: a reserved name and a place in storage for the bytes.

The row is created by POST /uploads (new file) or POST /files/{id}/replace,
and finished by POST /uploads/{id}/complete. Its state is in the fields:
pending until completed_at is set or expires_at passes.
"""

import uuid
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.core.api import iso
from apps.files.models import NAME_MAX_LENGTH, File

UPLOAD_TTL = timedelta(minutes=15)


class Upload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="uploads"
    )
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    mime_type = models.CharField(max_length=255)
    size_bytes = models.BigIntegerField()
    # The file being replaced, or, once complete, the file that was created.
    file = models.ForeignKey(
        File, null=True, blank=True, on_delete=models.CASCADE, related_name="uploads"
    )
    is_replace = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Upload of {self.name} by {self.owner}"

    @classmethod
    def start(
        cls, owner: User, name: str, mime_type: str, size_bytes: int, file: File | None = None
    ) -> "Upload":
        return cls.objects.create(
            owner=owner,
            name=name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            file=file,
            is_replace=file is not None,
            expires_at=timezone.now() + UPLOAD_TTL,
        )

    @classmethod
    def pending(cls, owner: User) -> "QuerySet[Upload]":
        """New-file uploads of owner that still reserve their name."""
        return cls.objects.filter(
            owner=owner, is_replace=False, completed_at=None, expires_at__gt=timezone.now()
        )

    @property
    def storage_key(self) -> str:
        return f"uploads/{self.id}"

    @property
    def is_done(self) -> bool:
        return self.completed_at is not None

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= timezone.now()


def to_json(upload: Upload, put_url: str) -> dict[str, Any]:
    return {
        "id": str(upload.id),
        "name": upload.name,
        "put_url": put_url,
        "put_headers": {"content-type": upload.mime_type},
        "expires_at": iso(upload.expires_at),
    }
