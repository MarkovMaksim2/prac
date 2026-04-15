from app.parsers.docx_parser import parse_docx
from docx import Document
import tempfile


def test_parse_docx_basic():
    doc = Document()
    doc.add_paragraph("Тест")

    with tempfile.NamedTemporaryFile(suffix=".docx") as tmp:
        doc.save(tmp.name)
        result = parse_docx(tmp.name)

    assert "paragraphs" in result
    assert len(result["paragraphs"]) == 1