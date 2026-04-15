from app.db.models import Batch, File, Error, Report
import uuid


def save_batch(db, user_id, batch_id, results, report_path, paths):
    batch = db.query(Batch).filter(Batch.id == batch_id and Batch.user_id == user_id).first()
    batch.status = "completed"

    for res in results:
        file = File(
            id=uuid.uuid4(),
            batch_id=batch.id,
            filename=res.filename,
            score=res.score,
            path=paths[res.filename]
        )
        db.add(file)

        for err in res.errors:
            db.add(Error(
                id=uuid.uuid4(),
                file_id=file.id,
                code=err.code,
                message=err.message,
                paragraph=err.paragraph
            ))

    report = Report(
        id=uuid.uuid4(),
        batch_id=batch.id,
        path=report_path
    )
    db.add(report)

    db.commit()