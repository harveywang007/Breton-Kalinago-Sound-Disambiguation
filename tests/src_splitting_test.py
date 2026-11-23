from unittest.mock import Mock

import pymupdf
import pytest

from src import constants, splitting


def test_create_folder_creates_directory(tmp_path):
    folder = tmp_path / "output"

    splitting.create_folder(str(folder))

    assert folder.is_dir()


def test_create_folder_accepts_existing_directory(tmp_path):
    folder = tmp_path / "output"

    splitting.create_folder(str(tmp_path))

    assert folder.is_dir()


def test_split_rejects_missing_input(tmp_path):
    missing_file = tmp_path / "missing.pdf"

    with pytest.raises(ValueError, match="This file doesn't exist!"):
        splitting.split(str(missing_file), str(tmp_path), section=[0, 1])
