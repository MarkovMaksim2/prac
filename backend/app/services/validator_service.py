from app.validators.structure import StructureValidator
from app.validators.formatting import FormattingValidator
from app.validators.numbering import NumberingValidator


class ValidatorService:

    def __init__(self):
        self.validators = [
            StructureValidator(),
            FormattingValidator(),
            NumberingValidator(),
        ]

    def validate(self, doc):
        errors = []

        for validator in self.validators:
            errors.extend(validator.validate(doc))

        score = max(0, 100 - len(errors))

        return errors, score