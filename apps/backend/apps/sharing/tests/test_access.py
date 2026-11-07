import pytest

from apps.sharing.access import Access, access_for

from .helpers import make_file, make_grant, make_link, make_user

ALL_THREE = frozenset({"view", "edit", "delete"})


@pytest.mark.django_db
def test_owner_holds_all_three() -> None:
    user = make_user()
    budget = make_file(user, "Q4 Budget.xls")

    assert access_for(user, budget) == Access(kind="owner", permissions=ALL_THREE)


@pytest.mark.django_db
def test_stranger_has_no_access() -> None:
    budget = make_file(make_user(), "Q4 Budget.xls")

    assert access_for(make_user("test_other_user"), budget) is None


@pytest.mark.django_db
def test_grantee_holds_what_the_link_gave() -> None:
    user = make_user()
    other_user = make_user("test_other_user")
    budget = make_file(user, "Q4 Budget.xls")
    make_grant(budget, other_user, make_link(budget, user, permissions=("view", "edit")))

    expected = Access(kind="granted", permissions=frozenset({"view", "edit"}))
    assert access_for(other_user, budget) == expected


@pytest.mark.django_db
def test_two_links_add_up() -> None:
    user = make_user()
    other_user = make_user("test_other_user")
    budget = make_file(user, "Q4 Budget.xls")
    make_grant(budget, other_user, make_link(budget, user, permissions=("view",)))
    make_grant(budget, other_user, make_link(budget, user, permissions=("view", "edit")))

    expected = Access(kind="granted", permissions=frozenset({"view", "edit"}))
    assert access_for(other_user, budget) == expected
