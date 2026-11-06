"""What a user may do with a file or folder, and why.

Mirrors the spec: an owner holds all six on their files and three on their
folders; a grantee holds the union of their grants; a folder on the path to a
shared file can only be opened.
"""

from dataclasses import dataclass
from typing import Literal

from apps.accounts.models import User
from apps.files.models import Node

from .models import Grant
from .permissions import ALL_PERMISSIONS, FOLDER_OWNER_PERMISSIONS, Permission

AccessKind = Literal["owner", "granted", "path"]


@dataclass(frozen=True)
class Access:
    kind: AccessKind
    permissions: frozenset[str]


def access_for(user: User, node: Node) -> Access | None:
    """The user's access to the node, or None if they can't see it at all."""
    if node.owner_id == user.id:
        held = frozenset(ALL_PERMISSIONS) if node.is_file else FOLDER_OWNER_PERMISSIONS
        return Access(kind="owner", permissions=held)

    if node.is_file:
        granted: set[str] = set()
        for grant in Grant.objects.filter(file=node, user=user):
            granted.update(grant.permissions)
        return Access(kind="granted", permissions=frozenset(granted)) if granted else None

    if _has_shared_file_below(user, node):
        return Access(kind="path", permissions=frozenset({Permission.VIEW}))
    return None


def _has_shared_file_below(user: User, folder: Node) -> bool:
    shared = Grant.objects.filter(user=user, file__owner_id=folder.owner_id).select_related("file")
    return any(any(ancestor.id == folder.id for ancestor in grant.file.path()) for grant in shared)
