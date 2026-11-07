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


def start_and_put(client: Client, user: User, name: str, body: bytes, mime_type: str) -> str:
    """Reserve one file and PUT its bytes; returns the upload id."""
    response = start_upload(
        client, user, {"name": name, "size_bytes": len(body), "mime_type": mime_type}
    )
    upload = response.json()["data"][0]
    assert client.put(upload["put_url"], data=body, content_type=mime_type).status_code == 200
    return str(upload["id"])


def complete(client: Client, upload_id: str) -> Any:
    return client.post(f"/api/v1/uploads/{upload_id}/complete")
