"""The File object the API returns everywhere, as the viewer sees it."""

from typing import Any

from apps.accounts.models import User
from apps.core.api import iso
from apps.sharing.access import access_for
from apps.sharing.models import Grant

from .models import File


def file_to_json(file: File, viewer: User) -> dict[str, Any]:
    access = access_for(viewer, file)
    if access is None:
        raise ValueError("the viewer has no access to this file")
    grants = [] if access.kind == "owner" else Grant.objects.filter(file=file, user=viewer)
    return {
        "id": str(file.id),
        "name": file.name,
        "owner_id": str(file.owner_id),
        "mime_type": file.mime_type,
        "size_bytes": file.size_bytes,
        "access": access.kind,
        "permissions": [p for p in ("view", "edit", "delete") if p in access.permissions],
        "is_shared": Grant.objects.filter(file=file).exists(),
        "modified_at": iso(file.modified_at),
        "grants": [
            {
                "link_id": str(grant.link_id),
                "permissions": list(grant.permissions),
                "granted_at": iso(grant.granted_at),
            }
            for grant in grants
        ],
    }
