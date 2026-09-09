from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_code = Column(String(50), nullable=False, index=True)
    rule_name = Column(String(100), nullable=False)
    severity = Column(String(20), default="ERROR")  # CRITICAL, ERROR, WARNING, INFO
    status = Column(String(20), default="FAILED")   # PASSED, FAILED
    target_field = Column(String(50), nullable=True)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("Document", back_populates="validation_results")
