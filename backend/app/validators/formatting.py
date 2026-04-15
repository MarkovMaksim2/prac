from app.validators.base import BaseValidator
from app.domain.models import ValidationError


class FormattingValidator(BaseValidator):

    def validate(self, doc):
        errors = []

        for p in doc["paragraphs"]:
            idx = p["index"]

            if p["alignment"] not in (3, None):
                errors.append(ValidationError(
                    code="ALIGNMENT",
                    message="Нет выравнивания по ширине",
                    paragraph=idx
                ))

            if p["indent"] and p["indent"].pt < 35:
                errors.append(ValidationError(
                    code="INDENT",
                    message="Неверный абзацный отступ",
                    paragraph=idx
                ))

            for r in p["runs"]:
                if r["font"] and r["font"] != "Times New Roman":
                    errors.append(ValidationError(
                        code="FONT",
                        message="Неверный шрифт",
                        paragraph=idx
                    ))

                if r["size"] and r["size"] < 12:
                    errors.append(ValidationError(
                        code="FONT_SIZE",
                        message="Маленький шрифт",
                        paragraph=idx
                    ))
            
            
            if "footer" not in doc or not doc["footer"]:
                errors.append(ValidationError(
                    code="NO_PAGINATION",
                    message="Отсутствует нумерация внизу страницы",
                    paragraph=None
                ))
            else:
                has_page_number = False
                for element in doc["footer"]:
                    if element.get("type") == "page_number" or "page" in element.get("text", "").lower():
                        has_page_number = True
                        break
                
                if not has_page_number:
                    errors.append(ValidationError(
                        code="NO_PAGINATION",
                        message="В нижнем колонтитуле отсутствует номер страницы",
                        paragraph=None
                    ))

        return errors