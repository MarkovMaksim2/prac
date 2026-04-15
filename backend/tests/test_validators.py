import uuid

from app.tasks.validation_task import process_batch_task
from app.validators.structure import StructureValidator
from app.validators.formatting import FormattingValidator


def test_structure_validator_missing():
    doc = {"full_text": "ВВЕДЕНИЕ"}

    validator = StructureValidator()
    errors = validator.validate(doc)

    assert len(errors) > 0


def test_formatting_validator_font():
    doc = {
        "paragraphs": [
            {
                "index": 0,
                "alignment": 0,
                "indent": None,
                "runs": [{"font": "Arial", "size": 10}]
            }
        ]
    }

    validator = FormattingValidator()
    errors = validator.validate(doc)

    assert len(errors) >= 1