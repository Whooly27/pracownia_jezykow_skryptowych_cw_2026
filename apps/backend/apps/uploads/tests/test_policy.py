import pytest

from apps.uploads.policy import (
    MAX_FILE_BYTES,
    Rejection,
    check_name,
    check_new_file,
    check_size,
    check_type,
    upload_policy,
)


def test_policy_matches_the_spec() -> None:
    policy = upload_policy()

    assert policy["max_file_bytes"] == 26214400
    assert policy["allowed_extensions"] == [
        "pdf", "png", "jpg", "jpeg", "gif", "webp", "doc", "docx", "xls", "xlsx",
        "ppt", "pptx", "odt", "ods", "odp", "rtf", "txt", "csv", "md",
    ]  # fmt: skip


@pytest.mark.parametrize(
    ("name", "mime_type"),
    [
        ("Raport.pdf", "application/pdf"),
        ("RAPORT.PDF", "application/pdf"),
        ("photo.jpeg", "image/jpeg"),
        ("photo.jpg", "image/jpeg"),
        ("notes.md", "text/markdown"),
    ],
)
def test_allowed_types_pass(name: str, mime_type: str) -> None:
    assert check_type(name, mime_type) is None


@pytest.mark.parametrize(
    ("name", "mime_type"),
    [
        ("setup.exe", "application/octet-stream"),
        ("noext", "text/plain"),
        ("a.pdf", "image/png"),
        ("a.pdf", ""),
    ],
)
def test_unsupported_types_are_rejected(name: str, mime_type: str) -> None:
    rejection = check_type(name, mime_type)

    assert rejection is not None
    assert rejection.code == "unsupported_file_type"
    assert rejection.message.startswith(name)


def test_exactly_max_size_passes() -> None:
    assert check_size(MAX_FILE_BYTES) is None


def test_one_byte_over_is_too_large() -> None:
    assert check_size(MAX_FILE_BYTES + 1) == Rejection(
        "file_too_large", "Files over 25 MB can't be uploaded."
    )


@pytest.mark.parametrize("size", [0, -1, "12", True, None, 1.5])
def test_size_must_be_a_positive_integer(size: object) -> None:
    rejection = check_size(size)

    assert rejection is not None
    assert rejection.code == "validation_failed"


@pytest.mark.parametrize("name", ["", "a/b.pdf", "x" * 252 + ".pdf"])
def test_bad_names_are_rejected(name: str) -> None:
    rejection = check_name(name)

    assert rejection is not None
    assert rejection.code == "validation_failed"


def test_check_new_file_reports_the_first_problem() -> None:
    assert check_new_file("a/b.exe", 0, "x").code == "validation_failed"  # type: ignore[union-attr]
    assert check_new_file("b.exe", 0, "x").code == "unsupported_file_type"  # type: ignore[union-attr]
    assert check_new_file("b.pdf", 0, "application/pdf").code == "validation_failed"  # type: ignore[union-attr]
    assert check_new_file("b.pdf", 10, "application/pdf") is None
