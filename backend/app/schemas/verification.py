from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from backend.app.schemas.document import ExtractedFieldDTO, ValidationResultDTO


class FieldUpdatePayload(BaseModel):
    field_name: str
    value: str


class BatchFieldUpdatePayload(BaseModel):
    fields: Dict[str, str]


class VerificationDecision(BaseModel):
    decision: str  # "APPROVE" or "REJECT"
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    edited_fields: Optional[Dict[str, str]] = None


class VerificationTaskRead(BaseModel):
    id: int
    document_id: int
    priority: str
    status: str
    assigned_to_id: Optional[int] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    # Embedded document context for quick listing
    file_name: Optional[str] = None
    village: Optional[str] = None
    survey_number: Optional[str] = None
    overall_confidence: Optional[float] = None

    class Config:
        from_attributes = True


class VerificationStudioDetail(BaseModel):
    task: VerificationTaskRead
    document_id: int
    file_name: str
    file_path: str
    mime_type: str
    raw_ocr_text: Optional[str] = None
    fields: List[ExtractedFieldDTO] = []
    validation_results: List[ValidationResultDTO] = []
