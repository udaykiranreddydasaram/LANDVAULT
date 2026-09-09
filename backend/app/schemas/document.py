from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ExtractedFieldDTO(BaseModel):
    field: str
    value: Optional[str] = None
    confidence: float
    source_text: Optional[str] = None
    verified: bool = False
    bounding_box: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ValidationResultDTO(BaseModel):
    id: Optional[int] = None
    rule_code: str
    rule_name: str
    severity: str
    status: str
    target_field: Optional[str] = None
    message: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DocumentRead(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_hash: str
    file_size_bytes: int
    mime_type: str
    document_type: str
    status: str
    ocr_provider: str
    uploaded_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentDetail(DocumentRead):
    raw_ocr_text: Optional[str] = None
    fields: List[ExtractedFieldDTO] = []
    validation_results: List[ValidationResultDTO] = []
    verification_task_id: Optional[int] = None
    land_record_id: Optional[int] = None
