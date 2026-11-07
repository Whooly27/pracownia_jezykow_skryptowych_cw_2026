from typing import Any

from django.test import Client

from apps.accounts.models import User


def list_files(client: Client, user: User, **params: Any) -> Any:
    client.force_login(user)
    return client.get("/api/v1/files", params)


def names(response: Any) -> list[str]:
    return [item["name"] for item in response.json()["data"]["items"]]
