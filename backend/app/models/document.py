from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), unique=True, index=True, nullable=False)  # SHA-256
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(50), nullable=False)
    document_type = Column(String(50), default="Pattadar Passbook / ROR")
    status = Column(String(30), default="UPLOADED", index=True) 
    # UPLOADED, PROCESSING, EXTRACTED, VALIDATION_FAILED, REQUIRES_VERIFICATION, VERIFIED, REJECTED
    raw_ocr_text = Column(Text, nullable=True)
    ocr_provider = Column(String(50), default="mock")
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    uploaded_by = relationship("User", back_populates="uploaded_documents", foreign_keys=[uploaded_by_id])
    land_record = relationship("LandRecord", back_populates="document", uselist=False, cascade="all, delete-orphan")
    fields = relationship("LandRecordField", back_populates="document", cascade="all, delete-orphan")
    validation_results = relationship("ValidationResult", back_populates="document", cascade="all, delete-orphan")
    verification_task = relationship("VerificationTask", back_populates="document", uselist=False, cascade="all, delete-orphan")
