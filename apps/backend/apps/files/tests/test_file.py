import uuid

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.models import User
from apps.files.models import File


def make_user(name: str = "test_user") -> User:
    return User.objects.create_user(email=f"{name}@example.com", display_name=name)


def make_file(owner: User, name: str) -> File:
    file = File(
        owner=owner,
        name=name,
        mime_type="text/plain",
        size_bytes=12,
        modified_at=timezone.now(),
    )
    file.full_clean()
    file.save()
    return file


@pytest.mark.django_db
def test_file_has_uuid_and_storage_key() -> None:
    file = make_file(make_user(), "Q4 Budget.xls")

    assert isinstance(file.id, uuid.UUID)
    assert file.storage_key == f"files/{file.id}"


@pytest.mark.django_db
@pytest.mark.parametrize("name", ["", "   ", "a/b", "x" * 256])
def test_name_rules(name: str) -> None:
    with pytest.raises(ValidationError) as e:
        make_file(make_user(), name)

    assert "name" in e.value.error_dict


@pytest.mark.django_db
def test_name_is_unique_per_owner() -> None:
    user = make_user()
    make_file(user, "Q4 Budget.xls")

    with pytest.raises(ValidationError) as e:
        make_file(user, "Q4 Budget.xls")

    assert e.value.error_dict["name"][0].code == "name_conflict"


@pytest.mark.django_db
def test_name_is_case_sensitive() -> None:
    user = make_user()
    make_file(user, "Budżet.xlsx")
    make_file(user, "budżet.xlsx")

    assert File.objects.filter(owner=user).count() == 2


@pytest.mark.django_db
def test_same_name_allowed_for_different_owners() -> None:
    make_file(make_user("test_user"), "Q4 Budget.xls")
    make_file(make_user("test_other_user"), "Q4 Budget.xls")

    assert File.objects.count() == 2
