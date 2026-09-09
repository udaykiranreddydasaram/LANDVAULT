from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    entity_name = Column(String(50), nullable=False, index=True)  # document, land_record, verification_task
    entity_id = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)       # UPLOAD, VERIFY, EDIT_FIELD, APPROVE, REJECT, DUPLICATE_FLAG
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    performed_by = relationship("User", back_populates="audit_actions")
