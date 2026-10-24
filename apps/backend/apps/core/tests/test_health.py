from unittest.mock import patch

import pytest
from django.db import DatabaseError
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_health_reports_ok_when_database_is_reachable(client: Client) -> None:
    response = client.get(reverse("core:health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


@pytest.mark.django_db
def test_health_reports_degraded_when_database_fails(client: Client) -> None:
    with patch("apps.core.views.connection.cursor", side_effect=DatabaseError):
        response = client.get(reverse("core:health"))

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "unavailable"}


def test_health_rejects_non_get(client: Client) -> None:
    response = client.post(reverse("core:health"))

    assert response.status_code == 405
