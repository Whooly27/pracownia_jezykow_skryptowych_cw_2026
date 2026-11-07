from pathlib import Path

import pytest
from django.conf import LazySettings


@pytest.fixture(autouse=True)
def blob_root(settings: LazySettings, tmp_path: Path) -> Path:
    settings.BLOB_ROOT = str(tmp_path)
    return tmp_path
