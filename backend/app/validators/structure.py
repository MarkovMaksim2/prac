from app.validators.base import BaseValidator
from app.domain.models import ValidationError

REQUIRED_ORDER = [
    "СОДЕРЖАНИЕ",
    "ВВЕДЕНИЕ",
    "СПИСОК СОКРАЩЕНИЙ И УСЛОВНЫХ ОБОЗНАЧЕНИЙ",
    "ТЕРМИНЫ И ОПРЕДЕЛЕНИЯ",
    "СПИСОК ИСПОЛЬЗОВАННЫХ МАТЕРИАЛОВ",
    "ЗАКЛЮЧЕНИЕ",
]


class StructureValidator(BaseValidator):

    def validate(self, doc):
        errors = []
        text = doc["full_text"].upper()

        last_pos = -1

        for section in REQUIRED_ORDER:
            pos = text.find(section)

            if pos == -1:
                errors.append(ValidationError(
                    code="STRUCT_MISSING",
                    message=f"Отсутствует раздел: {section}"
                ))
                continue

            if pos < last_pos:
                errors.append(ValidationError(
                    code="STRUCT_ORDER",
                    message=f"Нарушен порядок: {section}"
                ))

            last_pos = pos

        return errors