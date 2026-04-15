from app.workers.batch_processor import BatchProcessor


def test_batch_processor(monkeypatch):
    monkeypatch.setattr(
        "app.workers.batch_processor.parse_docx",
        lambda path: {"paragraphs": [], "full_text": ""}
    )

    processor = BatchProcessor()
    results = processor.process([{"name": "file.docx", "path": "x"}])

    assert len(results) == 1