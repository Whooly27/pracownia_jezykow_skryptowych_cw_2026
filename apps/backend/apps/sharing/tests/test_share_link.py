from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.models import User
from apps.sharing.models import Grant

from .helpers import make_file, make_folder, make_link


@pytest.mark.django_db
def test_link_records_file_permissions_creator_and_expiry() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    budget = make_file(user, "Q4 Budget.xls")
    expires = timezone.now() + timedelta(days=30)

    link = make_link(budget, user, permissions=("view", "edit", "rename"), expires_at=expires)

    assert link.file == budget
    assert link.created_by == user
    assert link.permissions == ["view", "edit", "rename"]
    assert link.expires_at == expires
    assert link.deleted_at is None


@pytest.mark.django_db
def test_link_without_expiry_never_expires() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    link = make_link(make_file(user, "a.txt"), user)

    assert link.expires_at is None
    assert not link.is_expired


@pytest.mark.django_db
def test_link_is_expired_after_expires_at() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    link = make_link(
        make_file(user, "a.txt"), user, expires_at=timezone.now() - timedelta(seconds=1)
    )

    assert link.is_expired


@pytest.mark.django_db
def test_link_must_target_a_file() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    with pytest.raises(ValidationError, match="file"):
        make_link(make_folder(user, "Acme Inc"), user)


@pytest.mark.django_db
def test_link_must_include_view() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    with pytest.raises(ValidationError, match="view"):
        make_link(make_file(user, "a.txt"), user, permissions=("link",))


@pytest.mark.django_db
def test_redemption_count_counts_grants_made_through_the_link() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    budget = make_file(user, "Q4 Budget.xls")
    link = make_link(budget, user)
    assert link.redemption_count == 0

    Grant.objects.create(
        file=budget,
        user=other_user,
        granted_by=user,
        permissions=["view"],
        via=Grant.Via.LINK,
        link=link,
    )

    assert link.redemption_count == 1
