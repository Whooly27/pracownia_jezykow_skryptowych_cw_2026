from typing import Any

from django.utils import timezone

from apps.accounts.models import User
from apps.files.models import File
from apps.sharing.models import Grant, ShareLink


def make_user(name: str = "test_user") -> User:
    return User.objects.create_user(email=f"{name}@example.com", display_name=name)


def make_file(owner: User, name: str) -> File:
    file = File(
        owner=owner, name=name, mime_type="text/plain", size_bytes=12, modified_at=timezone.now()
    )
    file.full_clean()
    file.save()
    return file


def make_link(
    file: File,
    created_by: User,
    permissions: tuple[str, ...] = ("view",),
    token_hash: str | None = None,
    **extra: Any,
) -> ShareLink:
    link = ShareLink(
        file=file,
        created_by=created_by,
        token_hash=token_hash or f"{ShareLink.objects.count():064d}",
        permissions=list(permissions),
        **extra,
    )
    link.full_clean()
    link.save()
    return link


def make_grant(
    file: File, user: User, link: ShareLink, permissions: tuple[str, ...] | None = None
) -> Grant:
    grant = Grant(
        file=file,
        user=user,
        link=link,
        permissions=list(permissions) if permissions is not None else list(link.permissions),
    )
    grant.full_clean()
    grant.save()
    return grant
