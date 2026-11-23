from unittest.mock import Mock

import pymupdf
import pytest

from src import constants, splitting


def test_create_folder_creates_directory(tmp_path):
    folder = tmp_path / "output"

    splitting.create_folder(str(folder))

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
    tmp_path, mockument, page_range, expected_pages
):
    source = tmp_path / "source.pdf"
    document = mockument

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

    assert (tmp_path / f"source - Introduction{constants.PDF_SUFFIX}").is_file()

    output = pymupdf.open(expected_path)
    try:
        assert len(output) == len(expected_pages)
        assert [page.get_text().strip() for page in output] == [
            f"This is sample text on page {page_num + 1} of the test PDF."
            for page_num in expected_pages
        ]
    finally:
        output.close()


def test_split_helper_skips_existing_output(tmp_path, mockument,capsys):
    source = tmp_path / "source.pdf"
    existing_output = tmp_path / f"source - Part{constants.PDF_SUFFIX}"
    existing_output.write_text("This should not change!", encoding="utf-8")
    existing_output.touch()

    document = mockument

    splitting.split_helper(
        document,
        str(source),
        str(tmp_path),
        "part",
        [0, 1],
    )

    assert existing_output.read_text(encoding="utf-8") == "This should not change!"

    captured = capsys.readouterr()
    assert f"{existing_output.name} exists. Skipping..." in captured.out


def test_split_opens_source_for_each_section(tmp_path, mockument):
    source = tmp_path / "source.pdf"
    mockument.save(str(source))
    mockument.close()

    result = splitting.split(
        str(source),
        str(tmp_path),
        introduction=[0, 1],
        appendix=[2, 3],
    )

    intro_path = tmp_path / f"source - Introduction{constants.PDF_SUFFIX}"
    appendix_path = tmp_path / f"source - Appendix{constants.PDF_SUFFIX}"

    assert result is None
    assert intro_path.is_file()
    assert appendix_path.is_file()

    intro = pymupdf.open(str(intro_path))
    appendix = pymupdf.open(str(appendix_path))
    try:
        assert [page.get_text().strip() for page in intro] == [
            "This is sample text on page 1 of the test PDF.",
            "This is sample text on page 2 of the test PDF.",
        ]
        assert [page.get_text().strip() for page in appendix] == [
            "This is sample text on page 3 of the test PDF.",
            "This is sample text on page 4 of the test PDF.",
        ]
    finally:
        intro.close()
        appendix.close()
