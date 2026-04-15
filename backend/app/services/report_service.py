from openpyxl import Workbook
import uuid
import os
from app.core.config import settings


def generate_report(results):
    wb = Workbook()
    ws = wb.active
    ws.append(["Файл", "Код", "Ошибка", "Параграф"])

    for res in results:
        for err in res.errors:
            ws.append([
                res.filename,
                err.code,
                err.message,
                err.paragraph
            ])

    path = os.path.join(settings.REPORT_DIR, f"{uuid.uuid4()}.xlsx")
    os.makedirs(settings.REPORT_DIR, exist_ok=True)

    wb.save(path)
    return path