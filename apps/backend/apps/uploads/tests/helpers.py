import json
from typing import Any

from django.test import Client

from apps.accounts.models import User

PDF = {"name": "Brand brief v2.pdf", "size_bytes": 1992294, "mime_type": "application/pdf"}


def post_json(client: Client, url: str, body: Any) -> Any:
    return client.post(url, data=json.dumps(body), content_type="application/json")


def start_upload(client: Client, user: User, *files: dict[str, Any]) -> Any:
    client.force_login(user)
    return post_json(client, "/api/v1/uploads", {"files": list(files)})
