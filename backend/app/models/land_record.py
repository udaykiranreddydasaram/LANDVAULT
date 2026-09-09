from datetime import datetime, date, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class LandRecord(Base):
    __tablename__ = "land_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False)
    record_identifier = Column(String(100), unique=True, index=True, nullable=False)
    
    # Administrative & Cadastral Fields
    state = Column(String(100), index=True, nullable=False)
    district = Column(String(100), index=True, nullable=False)
    mandal_tehsil = Column(String(100), index=True, nullable=False)
    village = Column(String(100), index=True, nullable=False)
    landowner_name = Column(String(255), index=True, nullable=False)
    survey_number = Column(String(50), index=True, nullable=False)
    khasra_number = Column(String(50), nullable=True)
    khata_number = Column(String(50), nullable=True)
    plot_number = Column(String(50), nullable=True)
    land_area = Column(Float, nullable=False)
    area_unit = Column(String(20), default="Acres", nullable=False)
    land_classification = Column(String(100), default="Agricultural - Dry")
    ownership_type = Column(String(50), default="Pattadar")
    mutation_number = Column(String(100), nullable=True)
    registration_number = Column(String(100), nullable=True)
    registration_date = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Verification & Quality Metas
    overall_confidence = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    is_disputed = Column(Boolean, default=False)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("Document", back_populates="land_record")
    verified_by = relationship("User", back_populates="verified_records", foreign_keys=[verified_by_id])
    gis_parcel = relationship("GISParcel", back_populates="land_record", uselist=False, cascade="all, delete-orphan")
