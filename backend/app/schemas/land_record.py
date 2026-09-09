from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class LandRecordBase(BaseModel):
    state: str
    district: str
    mandal_tehsil: str
    village: str
    landowner_name: str
    survey_number: str
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    plot_number: Optional[str] = None
    land_area: float
    area_unit: str = "Acres"
    land_classification: str = "Agricultural - Dry"
    ownership_type: str = "Pattadar"
    mutation_number: Optional[str] = None
    registration_number: Optional[str] = None
    registration_date: Optional[date] = None
    remarks: Optional[str] = None


class LandRecordCreate(LandRecordBase):
    document_id: int
    record_identifier: str
    overall_confidence: float = 0.0


class LandRecordUpdate(BaseModel):
    state: Optional[str] = None
    district: Optional[str] = None
    mandal_tehsil: Optional[str] = None
    village: Optional[str] = None
    landowner_name: Optional[str] = None
    survey_number: Optional[str] = None
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    plot_number: Optional[str] = None
    land_area: Optional[float] = None
    area_unit: Optional[str] = None
    land_classification: Optional[str] = None
    ownership_type: Optional[str] = None
    mutation_number: Optional[str] = None
    registration_number: Optional[str] = None
    registration_date: Optional[date] = None
    remarks: Optional[str] = None


class LandRecordRead(LandRecordBase):
    id: int
    document_id: int
    record_identifier: str
    overall_confidence: float
    is_verified: bool
    is_disputed: bool
    verified_by_id: Optional[int] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
