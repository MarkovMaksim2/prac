from app.parsers.docx_parser import parse_docx
from app.services.validator_service import ValidatorService
from app.domain.models import FileResult


class BatchProcessor:

    def __init__(self):
        self.validator = ValidatorService()

    def process(self, files):
        results = []

        for file in files:
            doc = parse_docx(file["path"])
            errors, score = self.validator.validate(doc)

            results.append(FileResult(
                filename=file["name"],
                errors=errors,
                score=score
            ))

        return results