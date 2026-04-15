import io
import uuid
import pytest

from app.api.deps import get_current_user_id
from app.db.models import User, Batch, File as Filedb, Report


@pytest.fixture
def test_user(db_session):
    user = User(
        id=uuid.uuid4(),
        email="test@test.com",
        password_hash="fake"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_override(app, test_user):
    app.dependency_overrides[get_current_user_id] = lambda: test_user.id
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_celery(monkeypatch):
    class FakeTask:
        id = "fake-task-id"

    def fake_delay(*args, **kwargs):
        return FakeTask()

    monkeypatch.setattr(
        "app.api.routes.process_batch_task.delay",
        fake_delay
    )


def test_validate_endpoint(client, auth_override, mock_celery):
    fake_file = io.BytesIO(b"fake content")

    response = client.post(
        "/validate",
        files={
            "files": (
                "test.docx",
                fake_file,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "batch_id" in data
    assert data["status"] == "processing"


def test_validate_too_many_files(client, auth_override):
    from app.core.config import settings

    files = [
        ("files", ("f.docx", io.BytesIO(b"data"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
        for _ in range(settings.MAX_FILES + 1)
    ]

    response = client.post("/validate", files=files)

    assert response.status_code == 200
    assert response.json()["error"] == "Too many files"


def test_validate_no_files(client, auth_override):
    response = client.post("/validate", files=[])
    assert response.status_code == 422


def test_get_batches(client, db_session, test_user):
    batch = Batch(
        id=uuid.uuid4(),
        user_id=test_user.id,
        total_files=1,
        status="completed"
    )
    db_session.add(batch)
    db_session.commit()

    response = client.get("/batches")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_batch(client, db_session, test_user):
    batch_id = uuid.uuid4()

    batch = Batch(
        id=batch_id,
        user_id=test_user.id,
        total_files=1,
        status="completed"
    )
    db_session.add(batch)

    file = Filedb(
        id=uuid.uuid4(),
        batch_id=batch_id,
        filename="test.docx",
        path="/tmp/test.docx",
        errors=[],
        score=95
    )
    db_session.add(file)
    db_session.commit()

    response = client.get(f"/batch/{str(batch_id)}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["total_files"] == 1
    assert len(data["files"]) == 1


def test_delete_batch_success(client, db_session, test_user, auth_override):
    batch_id = uuid.uuid4()

    batch = Batch(
        id=batch_id,
        user_id=test_user.id,
        total_files=1,
        status="completed"
    )
    db_session.add(batch)
    db_session.commit()

    response = client.delete(f"/batch/{str(batch_id)}")

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_delete_batch_not_found(client, auth_override):
    response = client.delete(f"/batch/{str(uuid.uuid4())}")
    assert response.json()["error"] == "Batch not found"


def test_delete_batch_forbidden(client, db_session, auth_override):
    other_user_id = uuid.uuid4()

    batch = Batch(
        id=uuid.uuid4(),
        user_id=other_user_id,
        total_files=1,
        status="completed"
    )
    db_session.add(batch)
    db_session.commit()

    response = client.delete(f"/batch/{str(batch.id)}")

    assert response.json()["error"] == "Forbidden"


def test_delete_batch_processing(client, db_session, test_user, auth_override):
    batch = Batch(
        id=uuid.uuid4(),
        user_id=test_user.id,
        total_files=1,
        status="processing"
    )
    db_session.add(batch)
    db_session.commit()

    response = client.delete(f"/batch/{batch.id}")

    assert response.json()["error"] == "Batch is still processing"


def test_get_report_success(client, db_session, test_user, auth_override, tmp_path):
    batch_id = uuid.uuid4()

    file_path = tmp_path / "report.xlsx"
    file_path.write_bytes(b"fake excel content")

    batch = Batch(
        id=batch_id,
        user_id=test_user.id,
        total_files=1,
        status="completed"
    )
    db_session.add(batch)

    report = Report(
        id=uuid.uuid4(),
        batch_id=batch_id,
        path=str(file_path)
    )
    db_session.add(report)
    db_session.commit()

    response = client.get(f"/report/{batch_id}")

    assert response.status_code == 200


def test_get_report_not_found(client, db_session, test_user, auth_override):
    batch_id = uuid.uuid4()

    batch = Batch(
        id=batch_id,
        user_id=test_user.id,
        total_files=1,
        status="completed"
    )
    db_session.add(batch)
    db_session.commit()

    response = client.get(f"/report/{batch_id}")

    assert response.json()["error"] == "Report not found"


def test_get_report_forbidden(client, db_session, auth_override, tmp_path):
    batch_id = uuid.uuid4()

    other_user_id = uuid.uuid4()

    file_path = tmp_path / "report.xlsx"
    file_path.write_bytes(b"fake")

    batch = Batch(
        id=batch_id,
        user_id=other_user_id,
        total_files=1,
        status="completed"
    )
    db_session.add(batch)

    report = Report(
        id=uuid.uuid4(),
        batch_id=batch_id,
        path=str(file_path)
    )
    db_session.add(report)
    db_session.commit()

    response = client.get(f"/report/{batch_id}")

    assert response.json()["error"] == "Forbidden"


def test_get_report_not_ready(client, db_session, test_user, auth_override):
    batch_id = uuid.uuid4()

    batch = Batch(
        id=batch_id,
        user_id=test_user.id,
        total_files=1,
        status="processing"
    )
    db_session.add(batch)

    report = Report(
        id=uuid.uuid4(),
        batch_id=batch_id,
        path="/tmp/fake.xlsx"
    )
    db_session.add(report)
    db_session.commit()

    response = client.get(f"/report/{batch_id}")

    assert response.json()["error"] == "Report is not ready yet"


def test_login_success(client, db_session):
    from app.db.models import User
    from app.services.auth_service import hash_password

    user = User(
        email="test@test.com",
        password_hash=hash_password("1234")
    )
    db_session.add(user)
    db_session.commit()

    response = client.post("/login", json={
        "email": "test@test.com",
        "password": "1234"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()
