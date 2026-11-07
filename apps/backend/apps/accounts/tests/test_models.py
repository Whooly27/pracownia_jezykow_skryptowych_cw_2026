import uuid

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models import User


def test_user_is_the_auth_user_model() -> None:
    assert get_user_model() is User


@pytest.mark.django_db
def test_user_has_uuid_primary_key_email_and_display_name() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")

    assert isinstance(user.id, uuid.UUID)
    assert user.email == "test_user@example.com"
    assert user.display_name == "test_user"
    assert user.get_username() == "test_user@example.com"
