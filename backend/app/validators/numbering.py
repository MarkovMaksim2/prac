import re
from app.validators.base import BaseValidator
from app.domain.models import ValidationError


class NumberingValidator(BaseValidator):

    def validate(self, doc):
        errors = []

        pattern = r"Рисунок\s+\d+"
        matches = re.findall(pattern, doc["full_text"])

        if not matches:
            errors.append(ValidationError(
                code="NO_FIGURES",
                message="Нет ни одного рисунка"
            ))

        return errors