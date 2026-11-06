import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.sharing.models import Grant

from .helpers import make_file, make_folder, make_grant, make_link


@pytest.mark.django_db
def test_grant_records_who_gave_what_to_whom() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    budget = make_file(user, "Q4 Budget.xls")

    grant = make_grant(budget, other_user, user, permissions=("view", "share"))

    assert grant.user == other_user
    assert grant.granted_by == user
    assert grant.permissions == ["view", "share"]
    assert grant.via == Grant.Via.DIRECT
    assert grant.link is None
    assert grant.granted_at is not None


@pytest.mark.django_db
def test_grant_must_target_a_file_not_a_folder() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    folder = make_folder(user, "Acme Inc")

    with pytest.raises(ValidationError, match="file"):
        make_grant(folder, other_user, user)


@pytest.mark.django_db
def test_grant_must_include_view() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    budget = make_file(user, "Q4 Budget.xls")

    with pytest.raises(ValidationError, match="view"):
        make_grant(budget, other_user, user, permissions=("edit",))


@pytest.mark.django_db
def test_owner_cannot_be_granted_their_own_file() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    budget = make_file(user, "Q4 Budget.xls")

    with pytest.raises(ValidationError, match="owner"):
        make_grant(budget, user, user)


@pytest.mark.django_db
def test_direct_grant_cannot_reference_a_link() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    budget = make_file(user, "Q4 Budget.xls")
    link = make_link(budget, user)

    with pytest.raises(ValidationError, match="link"):
        make_grant(budget, other_user, user, via=Grant.Via.DIRECT, link=link)


@pytest.mark.django_db
def test_link_grant_requires_a_link() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    budget = make_file(user, "Q4 Budget.xls")

    with pytest.raises(ValidationError, match="link"):
        make_grant(budget, other_user, user, via=Grant.Via.LINK)


@pytest.mark.django_db
def test_different_givers_can_each_grant_the_same_person() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    third_user = User.objects.create_user(
        email="test_third_user@example.com", display_name="test_third_user"
    )
    budget = make_file(user, "Q4 Budget.xls")

    make_grant(budget, third_user, user, permissions=("view", "share"))
    make_grant(budget, other_user, user, permissions=("view", "share"))
    make_grant(budget, third_user, other_user, permissions=("view",))

    assert Grant.objects.filter(file=budget, user=third_user).count() == 2
