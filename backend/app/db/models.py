import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    batches = relationship("Batch", back_populates="user")


class Batch(Base):
    __tablename__ = "batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    total_files = Column(Integer)
    status = Column(String, default="completed")
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="batches")
    files = relationship("File", back_populates="batch")
    report = relationship("Report", back_populates="batch", uselist=False)


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"))
    filename = Column(Text)
    score = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    path = Column(Text)

    batch = relationship("Batch", back_populates="files")
    errors = relationship("Error", back_populates="file")


class Error(Base):
    __tablename__ = "errors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"))
    code = Column(String)
    message = Column(Text)
    paragraph = Column(Integer)

    file = relationship("File", back_populates="errors")


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id", ondelete="CASCADE"))
    path = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    batch = relationship("Batch", back_populates="report")