from typing import Any

from apps.accounts.models import User
from apps.files.models import Node
from apps.sharing.models import Grant, ShareLink


def make_folder(owner: User, name: str, parent: Node | None = None) -> Node:
    node = Node(kind=Node.Kind.FOLDER, name=name, parent=parent, owner=owner)
    node.full_clean()
    node.save()
    return node


def make_file(owner: User, name: str, parent: Node | None = None) -> Node:
    node = Node(
        kind=Node.Kind.FILE,
        name=name,
        parent=parent,
        owner=owner,
        mime_type="text/plain",
        size_bytes=12,
    )
    node.full_clean()
    node.save()
    return node


def make_grant(
    file: Node,
    user: User,
    granted_by: User,
    permissions: tuple[str, ...] = ("view",),
    **extra: Any,
) -> Grant:
    grant = Grant(
        file=file, user=user, granted_by=granted_by, permissions=list(permissions), **extra
    )
    grant.full_clean()
    grant.save()
    return grant


def make_link(
    file: Node,
    created_by: User,
    permissions: tuple[str, ...] = ("view",),
    token_hash: str = "h" * 64,
    **extra: Any,
) -> ShareLink:
    link = ShareLink(
        file=file,
        created_by=created_by,
        token_hash=token_hash,
        permissions=list(permissions),
        **extra,
    )
    link.full_clean()
    link.save()
    return link
