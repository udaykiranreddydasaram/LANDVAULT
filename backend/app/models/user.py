from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default="viewer", nullable=False)  # admin, verifier, viewer
    department = Column(String(100), default="Revenue & Registration Department")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    uploaded_documents = relationship("Document", back_populates="uploaded_by", foreign_keys="Document.uploaded_by_id")
    verified_records = relationship("LandRecord", back_populates="verified_by", foreign_keys="LandRecord.verified_by_id")
    assigned_tasks = relationship("VerificationTask", back_populates="assigned_to", foreign_keys="VerificationTask.assigned_to_id")
    audit_actions = relationship("AuditLog", back_populates="performed_by")
