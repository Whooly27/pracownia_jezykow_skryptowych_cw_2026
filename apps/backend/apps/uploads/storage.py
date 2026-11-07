"""Where file bytes live.

The API never touches bytes itself: it hands the browser a signed PUT URL,
checks with ``head`` that the bytes arrived, and copies them under the
file's key. That is exactly the shape of Vercel Blob's signed URLs, so
``LocalBlobStorage`` can stand in for it in development and tests.
"""

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from django.conf import settings
from django.core import signing
from django.utils.module_loading import import_string

from apps.core.api import iso

PUT_TOKEN_SALT = "blob-put"  # noqa: S105  (a signing salt, not a secret)
GET_TOKEN_SALT = "blob-get"  # noqa: S105


@dataclass(frozen=True)
class StoredObject:
    size_bytes: int
    mime_type: str


class Storage(Protocol):
    def put_url(self, key: str, mime_type: str, size_bytes: int, expires_at: datetime) -> str:
        """A URL the browser PUTs the bytes to; valid until expires_at."""

    def get_url(self, key: str, filename: str, expires_at: datetime) -> str:
        """A URL that serves the bytes as an attachment named filename; valid until expires_at."""

    def head(self, key: str) -> StoredObject | None:
        """Size and type of what is stored under key, or None if nothing is."""

    def copy(self, src: str, dst: str) -> None:
        """Copy src over dst."""

    def delete(self, key: str) -> None:
        """Remove key; a missing key is fine."""


def get_storage() -> Storage:
    storage: Storage = import_string(settings.STORAGE_BACKEND)()
    return storage


class LocalBlobStorage:
    """Bytes on local disk under BLOB_ROOT, the MIME type in a sidecar file."""

    def put_url(self, key: str, mime_type: str, size_bytes: int, expires_at: datetime) -> str:
        token = signing.dumps(
            {
                "key": key,
                "mime_type": mime_type,
                "size_bytes": size_bytes,
                "expires_at": iso(expires_at),
            },
            salt=PUT_TOKEN_SALT,
        )
        return f"{settings.BLOB_BASE_URL}/api/v1/_blob/{key}?token={token}"

    def get_url(self, key: str, filename: str, expires_at: datetime) -> str:
        token = signing.dumps(
            {"key": key, "filename": filename, "expires_at": iso(expires_at)},
            salt=GET_TOKEN_SALT,
        )
        return f"{settings.BLOB_BASE_URL}/api/v1/_blob/{key}?token={token}"

    def head(self, key: str) -> StoredObject | None:
        path = self.path_for(key)
        if not path.is_file():
            return None
        return StoredObject(path.stat().st_size, self.mime_path(path).read_text())

    def copy(self, src: str, dst: str) -> None:
        source, target = self.path_for(src), self.path_for(dst)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        shutil.copyfile(self.mime_path(source), self.mime_path(target))

    def delete(self, key: str) -> None:
        path = self.path_for(key)
        path.unlink(missing_ok=True)
        self.mime_path(path).unlink(missing_ok=True)

    def path_for(self, key: str) -> Path:
        root = Path(settings.BLOB_ROOT).resolve()
        path = (root / key).resolve()
        if root not in path.parents:
            raise ValueError(f"key must stay under BLOB_ROOT: {key}")
        return path

    @staticmethod
    def mime_path(path: Path) -> Path:
        return path.with_name(path.name + ".mime")
