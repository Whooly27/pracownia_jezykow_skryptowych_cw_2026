"""What a user may do with a file, and why.

The owner holds all three permissions. Anyone else holds the union of the
grants they got through links, or nothing.
"""

from dataclasses import dataclass
from typing import Literal

from apps.accounts.models import User
from apps.files.models import File

from .models import Grant
from .permissions import ALL_PERMISSIONS

AccessKind = Literal["owner", "granted"]


@dataclass(frozen=True)
class Access:
    kind: AccessKind
    permissions: frozenset[str]


def access_for(user: User, file: File) -> Access | None:
    """The user's access to the file, or None if they can't see it at all."""
    if file.owner_id == user.id:
        return Access(kind="owner", permissions=frozenset(ALL_PERMISSIONS))

    granted: set[str] = set()
    for grant in Grant.objects.filter(file=file, user=user):
        granted.update(grant.permissions)
    return Access(kind="granted", permissions=frozenset(granted)) if granted else None
