import pytest
from django.core.exceptions import ValidationError

from apps.sharing.permissions import ALL_PERMISSIONS, validate_permissions


def test_there_are_exactly_three_permissions() -> None:
    assert ALL_PERMISSIONS == ("view", "edit", "delete")


def test_validate_accepts_a_set_with_view() -> None:
    validate_permissions(["view", "edit"])


def test_validate_rejects_a_set_without_view() -> None:
    with pytest.raises(ValidationError):
        validate_permissions(["edit"])


def test_validate_rejects_unknown_permission() -> None:
    with pytest.raises(ValidationError):
        validate_permissions(["view", "fly"])


def test_validate_rejects_rename() -> None:
    with pytest.raises(ValidationError):
        validate_permissions(["view", "rename"])
