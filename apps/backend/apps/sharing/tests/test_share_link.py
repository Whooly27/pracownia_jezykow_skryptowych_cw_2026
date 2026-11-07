from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from .helpers import make_file, make_grant, make_link, make_user


@pytest.mark.django_db
def test_link_records_file_permissions_creator_and_expiry() -> None:
    user = make_user()
    budget = make_file(user, "Q4 Budget.xls")
    expires = timezone.now() + timedelta(days=7)

    link = make_link(budget, user, permissions=("view", "edit"), expires_at=expires)

    assert link.file == budget
    assert link.permissions == ["view", "edit"]
    assert link.created_by == user
    assert link.expires_at == expires
    assert not link.is_expired
    assert not link.is_deleted


@pytest.mark.django_db
def test_link_without_expiry_never_expires() -> None:
    user = make_user()
    link = make_link(make_file(user, "a.txt"), user)

    assert link.expires_at is None
    assert not link.is_expired


@pytest.mark.django_db
def test_link_is_expired_after_expires_at() -> None:
    user = make_user()
    link = make_link(
        make_file(user, "a.txt"), user, expires_at=timezone.now() - timedelta(seconds=1)
    )

    assert link.is_expired


@pytest.mark.django_db
def test_link_must_include_view() -> None:
    user = make_user()
    with pytest.raises(ValidationError):
        make_link(make_file(user, "a.txt"), user, permissions=("edit",))


@pytest.mark.django_db
def test_redemption_count_counts_grants_made_through_the_link() -> None:
    user = make_user()
    budget = make_file(user, "Q4 Budget.xls")
    link = make_link(budget, user)
    make_grant(budget, make_user("test_other_user"), link)
    make_grant(budget, make_user("test_third_user"), link)

    assert link.redemption_count == 2
