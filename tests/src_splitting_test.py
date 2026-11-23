from unittest.mock import Mock, patch, call

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


def test_split_rejects_no_section_input(tmp_path):
    source = tmp_path / "source.pdf"
    source.touch()

    with pytest.raises(ValueError, match="No page ranges provided for splitting."):
        splitting.split(str(source), str(tmp_path))


@pytest.mark.parametrize("page_range", ([0, 0], (0, 0)))
def test_split_helper_rejects_empty_document(tmp_path, page_range):
    document = Mock()
    document.__len__ = Mock(return_value=0)

    with pytest.raises(ValueError, match="This file is empty!"):
        splitting.split_helper(
            document,
            str(tmp_path / "source.pdf"),
            str(tmp_path),
            "section",
            page_range,
        )

    document.close.assert_called_once_with()
    document.select.assert_not_called()
    document.save.assert_not_called()


@pytest.fixture
def mockument():
    doc = pymupdf.open()

    for i in range(7):
        page = doc.new_page()
        text = f"This is sample text on page {i + 1} of the test PDF."

        page.insert_text((72, 72), text, fontsize=14)

    return doc


@pytest.mark.parametrize(
    ("page_range", "expected_pages"),
    [
        ([1, 3], [1, 2, 3]),
        ((0, 2), [0, 1, 2]),
    ],
)
def test_split_helper_selects_saves_and_closes_document(
    tmp_path, page_range, expected_pages
):
    source = tmp_path / "source.pdf"
    document = mockument()

    splitting.split_helper(
        document,
        str(source),
        str(tmp_path),
        "introduction",
        page_range,
    )

    expected_path = str(
        tmp_path / f"source - Introduction{constants.PDF_SUFFIX}"
    )
    document.select.assert_called_once_with(expected_pages)
    document.save.assert_called_once_with(expected_path)
    document.close.assert_called_once_with()


def test_split_helper_skips_existing_output(tmp_path, capsys):
    source = tmp_path / "source.pdf"
    existing_output = tmp_path / f"source - Part{constants.PDF_SUFFIX}"
    existing_output.touch()

    document = mockument()

    splitting.split_helper(
        document,
        str(source),
        str(tmp_path),
        "part",
        [0, 1],
    )

    document.select.assert_called_once_with([0, 1])
    document.save.assert_not_called()
    document.close.assert_called_once_with()
    assert "source - Part.pdf exists. Skipping..." in capsys.readouterr().out


def test_split_opens_source_for_each_section(tmp_path):
    source = tmp_path / "source.pdf"
    source.touch()

    first_part = mockument()
    second_part = mockument()

    with patch.object(
        pymupdf,
        "open",
        side_effect=[first_part, second_part],
    ) as open_mock:
        result = splitting.split(
            str(source),
            str(tmp_path),
            introduction=[0, 1],
            appendix=[2, 3],
        )

    assert result is None
    assert open_mock.call_args_list == [call(str(source)), call(str(source))]
    first_part.select.assert_called_once_with([0, 1])
    second_part.select.assert_called_once_with([2, 3])
    first_part.save.assert_called_once_with(
        str(tmp_path / f"source - Introduction{constants.PDF_SUFFIX}")
    )
    second_part.save.assert_called_once_with(
        str(tmp_path / f"source - Appendix{constants.PDF_SUFFIX}")
    )
