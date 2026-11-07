import pytest
from django.core.exceptions import ValidationError

from .helpers import make_file, make_grant, make_link, make_user


@pytest.mark.django_db
def test_grant_records_who_joined_through_which_link() -> None:
    user = make_user()
    other_user = make_user("test_other_user")
    budget = make_file(user, "Q4 Budget.xls")
    link = make_link(budget, user, permissions=("view", "edit"))

    grant = make_grant(budget, other_user, link)

    assert grant.file == budget
    assert grant.user == other_user
    assert grant.link == link
    assert grant.permissions == ["view", "edit"]
    assert grant.granted_at is not None


@pytest.mark.django_db
def test_grant_copies_the_link_permissions() -> None:
    user = make_user()
    budget = make_file(user, "Q4 Budget.xls")
    link = make_link(budget, user, permissions=("view", "edit"))

    with pytest.raises(ValidationError) as e:
        make_grant(budget, make_user("test_other_user"), link, permissions=("view",))

    assert "permissions" in e.value.error_dict


@pytest.mark.django_db
def test_owner_cannot_be_granted_their_own_file() -> None:
    user = make_user()
    budget = make_file(user, "Q4 Budget.xls")
    link = make_link(budget, user)

    with pytest.raises(ValidationError):
        make_grant(budget, user, link)


@pytest.mark.django_db
def test_same_person_cannot_join_the_same_link_twice() -> None:
    user = make_user()
    other_user = make_user("test_other_user")
    budget = make_file(user, "Q4 Budget.xls")
    link = make_link(budget, user)
    make_grant(budget, other_user, link)

    with pytest.raises(ValidationError):
        make_grant(budget, other_user, link)
