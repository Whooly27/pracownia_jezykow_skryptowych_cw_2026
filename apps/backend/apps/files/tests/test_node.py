import uuid

import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.files.models import Node


def make_folder(owner: User, name: str, parent: Node | None = None) -> Node:
    node = Node(kind=Node.Kind.FOLDER, name=name, parent=parent, owner=owner)
    node.full_clean()
    node.save()
    return node


def make_file(owner: User, name: str, parent: Node | None = None) -> Node:
    node = Node(
        kind=Node.Kind.FILE,
        name=name,
        parent=parent,
        owner=owner,
        mime_type="text/plain",
        size_bytes=12,
    )
    node.full_clean()
    node.save()
    return node


@pytest.mark.django_db
def test_top_level_folder_has_uuid_and_empty_path() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    folder = make_folder(user, "Acme Inc")

    assert isinstance(folder.id, uuid.UUID)
    assert folder.parent is None
    assert folder.path() == []


@pytest.mark.django_db
def test_path_lists_ancestors_top_first() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    acme = make_folder(user, "Acme Inc")
    design = make_folder(user, "Design", parent=acme)
    budget = make_file(user, "Q4 Budget.xls", parent=design)

    assert budget.path() == [acme, design]


@pytest.mark.django_db
def test_folder_rejects_file_fields() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    folder = Node(kind=Node.Kind.FOLDER, name="Acme Inc", owner=user, mime_type="text/plain")

    with pytest.raises(ValidationError, match="mime_type"):
        folder.full_clean()


@pytest.mark.django_db
def test_file_requires_mime_type_and_size() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    file = Node(kind=Node.Kind.FILE, name="notes.txt", owner=user)

    with pytest.raises(ValidationError) as excinfo:
        file.full_clean()

    assert set(excinfo.value.message_dict) >= {"mime_type", "size_bytes"}


@pytest.mark.django_db
@pytest.mark.parametrize("name", ["", "   ", "a/b", "x" * 256])
def test_name_rules(name: str) -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    folder = Node(kind=Node.Kind.FOLDER, name=name, owner=user)

    with pytest.raises(ValidationError, match="name"):
        folder.full_clean()


@pytest.mark.django_db
def test_name_is_unique_within_a_folder() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    acme = make_folder(user, "Acme Inc")
    make_folder(user, "Assets", parent=acme)

    with pytest.raises(ValidationError, match="name"):
        make_file(user, "Assets", parent=acme)


@pytest.mark.django_db
def test_same_name_allowed_in_different_folders() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    acme = make_folder(user, "Acme Inc")
    design = make_folder(user, "Design", parent=acme)

    make_file(user, "notes.txt", parent=acme)
    make_file(user, "notes.txt", parent=design)


@pytest.mark.django_db
def test_same_name_allowed_for_different_owners() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    make_folder(user, "Acme Inc")
    make_folder(other_user, "Acme Inc")


@pytest.mark.django_db
def test_parent_must_be_a_folder() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    file = make_file(user, "notes.txt")
    child = Node(kind=Node.Kind.FOLDER, name="Inside", parent=file, owner=user)

    with pytest.raises(ValidationError, match="parent"):
        child.full_clean()


@pytest.mark.django_db
def test_parent_must_belong_to_the_same_owner() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    other_user = User.objects.create_user(
        email="test_other_user@example.com", display_name="test_other_user"
    )
    acme = make_folder(user, "Acme Inc")
    child = Node(kind=Node.Kind.FOLDER, name="Other", parent=acme, owner=other_user)

    with pytest.raises(ValidationError, match="parent"):
        child.full_clean()


@pytest.mark.django_db
def test_folder_cannot_be_moved_under_itself() -> None:
    user = User.objects.create_user(email="test_user@example.com", display_name="test_user")
    acme = make_folder(user, "Acme Inc")
    design = make_folder(user, "Design", parent=acme)
    acme.parent = design

    with pytest.raises(ValidationError, match="parent"):
        acme.full_clean()
