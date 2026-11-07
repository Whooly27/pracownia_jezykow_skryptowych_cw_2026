import pytest

from apps.files.serializers import file_to_json
from apps.sharing.tests.helpers import make_file, make_grant, make_link, make_user


@pytest.mark.django_db
def test_owner_json_has_all_three_permissions_and_member_count_1() -> None:
    user = make_user()
    budget = make_file(user, "Q4 Budget.xls")

    data = file_to_json(budget, user)

    assert data == {
        "id": str(budget.id),
        "name": "Q4 Budget.xls",
        "owner_id": str(user.id),
        "mime_type": "text/plain",
        "size_bytes": 12,
        "access": "owner",
        "permissions": ["view", "edit", "delete"],
        "is_shared": False,
        "modified_at": budget.modified_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "grants": [],
    }


@pytest.mark.django_db
def test_grantee_json_lists_their_grants_and_marks_the_file_shared() -> None:
    user = make_user()
    kate = make_user("test_kate")
    jo = make_user("test_jo")
    budget = make_file(user, "Q4 Budget.xls")
    view_link = make_link(budget, user, permissions=("view",))
    edit_link = make_link(budget, user, permissions=("view", "edit"))
    make_grant(budget, kate, view_link)
    kate_edit = make_grant(budget, kate, edit_link)
    make_grant(budget, jo, view_link)

    data = file_to_json(budget, kate)

    assert data["access"] == "granted"
    assert data["permissions"] == ["view", "edit"]
    assert data["is_shared"] is True
    assert file_to_json(budget, user)["is_shared"] is True
    assert [g["link_id"] for g in data["grants"]] == [str(view_link.id), str(edit_link.id)]
    assert data["grants"][1] == {
        "link_id": str(edit_link.id),
        "permissions": ["view", "edit"],
        "granted_at": kate_edit.granted_at.replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    }


@pytest.mark.django_db
def test_json_for_stranger_raises_value_error() -> None:
    budget = make_file(make_user(), "Q4 Budget.xls")

    with pytest.raises(ValueError, match="access"):
        file_to_json(budget, make_user("test_other_user"))
