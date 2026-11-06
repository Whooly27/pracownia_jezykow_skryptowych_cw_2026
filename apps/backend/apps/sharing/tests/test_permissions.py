import pytest
from django.core.exceptions import ValidationError

from apps.sharing.permissions import (
    validate_permissions,
)


def test_validate_accepts_a_set_with_view() -> None:
    validate_permissions(["view", "share"])


def test_validate_rejects_a_set_without_view() -> None:
    with pytest.raises(ValidationError, match="view"):
        validate_permissions(["edit"])


def test_validate_rejects_unknown_permission() -> None:
    with pytest.raises(ValidationError, match="unknown"):
        validate_permissions(["view", "admin"])
