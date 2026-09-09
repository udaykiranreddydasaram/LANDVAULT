from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class LandRecordField(Base):
    __tablename__ = "land_record_fields"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    field_name = Column(String(50), nullable=False, index=True)
    extracted_value = Column(Text, nullable=True)
    normalized_value = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    source_text = Column(Text, nullable=True)
    bounding_box = Column(JSON, nullable=True)  # {"x": float, "y": float, "width": float, "height": float, "page": int}
    is_verified = Column(Boolean, default=False)
    verified_value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("Document", back_populates="fields")
