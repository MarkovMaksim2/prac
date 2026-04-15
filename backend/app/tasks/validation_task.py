from app.core.celery_app import celery_app
from app.workers.batch_processor import BatchProcessor
from app.services.report_service import generate_report
from app.services.persistence_service import save_batch
from app.db.session import SessionLocal


@celery_app.task
def process_batch_task(files, user_id, batch_id):
    db = SessionLocal()

    try:
        processor = BatchProcessor()
        results = processor.process(files)

        report_path = generate_report(results)
        
        paths = {f["name"]: f["path"] for f in files}

        save_batch(db, user_id, batch_id, results, report_path, paths)

        return {"status": "completed"}

    except Exception as e:
        return {"status": "failed", "error": str(e)}

    finally:
        db.close()