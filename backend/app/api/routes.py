from fastapi import APIRouter, UploadFile, File, Depends
import os
import uuid
from uuid import UUID

from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.config import settings
from app.tasks.validation_task import process_batch_task
from app.db.session import get_db
from app.db.models import Batch, File as Filedb, Report
from fastapi.responses import FileResponse

router = APIRouter()


@router.post("/validate")
async def validate(
    files: list[UploadFile] = File(...),
    user_id: int = Depends(get_current_user_id),
    db=Depends(get_db)
):
    if len(files) > settings.MAX_FILES:
        return {"error": "Too many files"}

    saved_files = []

    for f in files:
        path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}.docx")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        with open(path, "wb") as buffer:
            buffer.write(await f.read())

        saved_files.append({
            "name": f.filename,
            "path": path
        })

    batch = Batch(
        id=uuid.uuid4(),
        user_id=user_id,
        total_files=len(saved_files),
        status="processing"
    )
    db.add(batch)
    db.commit()

    task = process_batch_task.delay(saved_files, user_id, batch.id)

    return {
        "batch_id": str(batch.id),
        "task_id": task.id,
        "status": "processing"
    }

@router.get("/batches")
def get_batches(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return db.query(Batch).filter(Batch.user_id == user_id).all()


@router.get("/batch/{batch_id}")
def get_batch(batch_id: UUID, db=Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    info = {}
    
    all_files = db.query(Filedb).filter(Filedb.batch_id == batch_id).all()
    for f in all_files:
        info[f.id] = {
            'errors': f.errors,
            'name': f.filename,
            'score': f.score
        }

    return {
        "status": batch.status,
        "total_files": batch.total_files,
        "files": info
    }

@router.delete("/batch/{batch_id}")
def delete_batch(
    batch_id: UUID,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()

    if not batch:
        return {"error": "Batch not found"}

    if batch.user_id != user_id:
        return {"error": "Forbidden"}
    
    if batch.status == "processing":
        return {"error": "Batch is still processing"}

    files = db.query(Filedb).filter(Filedb.batch_id == batch_id).all()

    for f in files:
        try:
            if f.path and os.path.exists(f.path):
                os.remove(f.path)
        except Exception as e:
            print(f"Error deleting file {f.path}: {e}")

    report_path = getattr(batch, "report_path", None)
    if report_path and os.path.exists(report_path):
        try:
            os.remove(report_path)
        except Exception as e:
            print(f"Error deleting report {report_path}: {e}")

    db.query(Filedb).filter(Filedb.batch_id == batch_id).delete()

    db.delete(batch)
    db.commit()

    return {"status": "deleted"}

@router.get("/report/{batch_id}")
def get_report(
    batch_id: UUID,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.batch_id == batch_id).first()
    batch = db.query(Batch).filter(Batch.id == batch_id).first()

    if not report:
        return {"error": "Report not found"}
    if not batch:
        return {"error": "Batch not found"}

    if batch.user_id != user_id:
        return {"error": "Forbidden"}

    if batch.status != "completed":
        return {"error": "Report is not ready yet"}

    report_path = report.path

    if not report_path or not os.path.exists(report_path):
        return {"error": "Report file not found"}

    return FileResponse(
        path=report_path,
        filename=f"report_{batch_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )