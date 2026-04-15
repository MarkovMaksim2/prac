import os

from app.domain.models import FileResult, ValidationError
from app.services.report_service import generate_report
from app.services.validator_service import ValidatorService


def test_validator_service():
    doc = {
        "full_text": "",
        "paragraphs": []
    }

    service = ValidatorService()
    errors, score = service.validate(doc)

    assert isinstance(errors, list)
    assert isinstance(score, int)

def test_generate_report():
    results = [
        FileResult(
            filename="test.docx",
            score=90,
            errors=[
                ValidationError(
                    code="FONT",
                    message="Ошибка шрифта",
                    paragraph=1
                )
            ]
        )
    ]

    path = generate_report(results)

    assert os.path.exists(path)

    os.remove(path)