import pytest
from pathlib import Path

from app.core.extraction import extract_text_from_file


# ------------------------------------------------
# Fixtures: dynamically created files
# ------------------------------------------------

@pytest.fixture
def temp_pdf(tmp_path):
    """Create a small randomly generated PDF document"""
    file_path = tmp_path / "temp.pdf"
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(file_path))
    c.drawString(210, 800, "HELLO PDF")
    c.save()
    return file_path


@pytest.fixture
def temp_docx(tmp_path):
    """Create a small randomly generated Word document"""
    file_path = tmp_path / "temp.docx"
    from docx import Document
    doc = Document()
    doc.add_paragraph("HELLO WORD")
    doc.save(file_path)
    return file_path


@pytest.fixture
def empty_file(tmp_path):
    """Create empty file"""
    file_path = tmp_path / "temp.txt"
    file_path.touch()
    return file_path


# ------------------------------------------------
# Test functions: use path input
# ------------------------------------------------
def test_temp_pdf_path(temp_pdf):
    markdown = extract_text_from_file(str(temp_pdf))
    assert isinstance(markdown, str)
    assert "HELLO PDF" in markdown


def test_temp_docx_path(temp_docx):
    markdown = extract_text_from_file(str(temp_docx))
    assert isinstance(markdown, str)
    assert "HELLO WORD" in markdown


def test_empty_file_path(empty_file):
    markdown = extract_text_from_file(str(empty_file))
    assert isinstance(markdown, str)
    assert markdown == ""


# ------------------------------------------------
# Test functions: use BinaryIO input
# ------------------------------------------------
def test_temp_pdf_stream(temp_pdf):
    with open(temp_pdf, "rb") as f:
        markdown = extract_text_from_file(f)
    assert isinstance(markdown, str)
    assert "HELLO PDF" in markdown


def test_temp_docx_stream(temp_docx):
    with open(temp_docx, "rb") as f:
        markdown = extract_text_from_file(f)
    assert isinstance(markdown, str)
    assert "HELLO WORD" in markdown


def test_empty_file_stream(empty_file):
    with open(empty_file, "rb") as f:
        markdown = extract_text_from_file(f)
    assert isinstance(markdown, str)
    assert markdown == ""


# ------------------------------------------------
# Parametrized test for real files
# ------------------------------------------------
TEST_FILES_DIR = Path(__file__).parent.parent / "files"
files = list(TEST_FILES_DIR.glob("*"))


@pytest.mark.parametrize("file_path", files)
def test_real_files_path(file_path):
    markdown = extract_text_from_file(str(file_path))
    assert isinstance(markdown, str)
    assert len(markdown) >= 0  # may be empty for some formats


@pytest.mark.parametrize("file_path", files)
def test_real_files_stream(file_path):
    with open(file_path, "rb") as f:
        markdown = extract_text_from_file(f)
    assert isinstance(markdown, str)
    assert len(markdown) >= 0
