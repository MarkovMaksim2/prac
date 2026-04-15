from pydantic import BaseModel
from typing import List


class ValidationError(BaseModel):
    code: str
    message: str
    paragraph: int | None = None


class FileResult(BaseModel):
    filename: str
    errors: List[ValidationError]
    score: int


class BatchResult(BaseModel):
    results: List[FileResult]
    total_files: int