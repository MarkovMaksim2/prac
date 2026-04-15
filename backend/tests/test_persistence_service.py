import uuid
from app.services.persistence_service import save_batch
from app.domain.models import FileResult, ValidationError
from app.db.models import Batch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base


def get_test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_save_batch():
    db = get_test_db()

    batch = Batch(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        total_files=1,
        status="processing"
    )
    db.add(batch)
    db.commit()

    results = [
        FileResult(
            filename="file.docx",
            score=80,
            errors=[
                ValidationError(
                    code="ERR",
                    message="Test error",
                    paragraph=1
                )
            ]
        )
    ]

    save_batch(db, batch.user_id, batch.id, results, "report.xlsx", {"file.docx": "file.docx"})

    saved_batch = db.query(Batch).first()

    assert saved_batch.status == "completed"