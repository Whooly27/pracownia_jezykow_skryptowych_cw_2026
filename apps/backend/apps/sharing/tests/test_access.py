import pytest

from apps.accounts.models import User
from apps.sharing.access import Access, access_for
from apps.sharing.models import Grant

from .helpers import make_file, make_folder, make_grant, make_link

ALL_SIX = frozenset({"view", "edit", "rename", "delete", "share", "link"})


@pytest.mark.django_db
def test_owner_holds_all_six_on_their_file() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    budget = make_file(user, "Q4 Budget.xls")

    assert access_for(user, budget) == Access(kind="owner", permissions=ALL_SIX)


@pytest.mark.django_db
def test_owner_holds_view_rename_delete_on_their_folder() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    folder = make_folder(user, "Acme Inc")

    expected = Access(kind="owner", permissions=frozenset({"view", "rename", "delete"}))
    assert access_for(user, folder) == expected


@pytest.mark.django_db
def test_stranger_has_no_access() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    budget = make_file(user, "Q4 Budget.xls")

    assert access_for(other_user, budget) is None


@pytest.mark.django_db
def test_grantee_holds_what_they_were_given() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    budget = make_file(user, "Q4 Budget.xls")
    make_grant(budget, other_user, user, permissions=("view", "share"))

    expected = Access(kind="granted", permissions=frozenset({"view", "share"}))
    assert access_for(other_user, budget) == expected


@pytest.mark.django_db
def test_two_grants_add_up() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    budget = make_file(user, "Q4 Budget.xls")
    link = make_link(budget, user, permissions=("view", "edit"))
    make_grant(budget, other_user, user, permissions=("view",))
    make_grant(
        budget, other_user, user, permissions=("view", "edit"), via=Grant.Via.LINK, link=link
    )

    expected = Access(kind="granted", permissions=frozenset({"view", "edit"}))
    assert access_for(other_user, budget) == expected


@pytest.mark.django_db
def test_folder_on_the_path_to_a_shared_file_is_viewable() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    acme = make_folder(user, "Acme Inc")
    design = make_folder(user, "Design", parent=acme)
    budget = make_file(user, "Q4 Budget.xls", parent=design)
    make_grant(budget, other_user, user)

    expected = Access(kind="path", permissions=frozenset({"view"}))
    assert access_for(other_user, design) == expected
    assert access_for(other_user, acme) == expected


@pytest.mark.django_db
def test_sibling_folder_is_not_viewable() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    acme = make_folder(user, "Acme Inc")
    design = make_folder(user, "Design", parent=acme)
    marketing = make_folder(user, "Marketing", parent=acme)
    make_grant(make_file(user, "Q4 Budget.xls", parent=design), other_user, user)

    assert access_for(other_user, marketing) is None


@pytest.mark.django_db
def test_other_files_in_a_path_folder_stay_hidden() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    design = make_folder(user, "Design")
    make_grant(make_file(user, "Q4 Budget.xls", parent=design), other_user, user)
    secret = make_file(user, "Salaries.xls", parent=design)

    assert access_for(other_user, secret) is None
