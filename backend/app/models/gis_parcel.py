from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class GISParcel(Base):
    __tablename__ = "gis_parcels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    land_record_id = Column(Integer, ForeignKey("land_records.id", ondelete="CASCADE"), unique=True, nullable=False)
    survey_number = Column(String(50), index=True, nullable=False)
    village = Column(String(100), index=True, nullable=False)
    mandal_tehsil = Column(String(100), nullable=True)
    district = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)
    geojson_geometry = Column(JSON, nullable=False)  # GeoJSON Polygon / MultiPolygon
    area_sq_meters = Column(Float, nullable=False)
    status = Column(String(30), default="VERIFIED")  # VERIFIED, PENDING_REVIEW, DISPUTED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    land_record = relationship("LandRecord", back_populates="gis_parcel")
