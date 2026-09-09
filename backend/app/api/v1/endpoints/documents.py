import os
import shutil
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db, get_current_user
from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.land_record import LandRecord
from backend.app.models.land_record_field import LandRecordField
from backend.app.models.validation_result import ValidationResult
from backend.app.models.verification_task import VerificationTask
from backend.app.models.gis_parcel import GISParcel
from backend.app.schemas.document import DocumentRead, DocumentDetail, ExtractedFieldDTO, ValidationResultDTO
from backend.app.services.duplicate.detector import calculate_sha256, DuplicateDetector
from backend.app.services.ocr.mock_provider import MockSmartOCRProvider
from backend.app.services.extraction.extractor import FieldExtractor
from backend.app.services.validation.engine import ValidationEngine
from backend.app.services.gis.parcel_builder import CadastralParcelBuilder
from backend.app.services.audit.logger import AuditLogger

router = APIRouter()
ocr_provider = MockSmartOCRProvider()
field_extractor = FieldExtractor()
parcel_builder = CadastralParcelBuilder()


async def process_document_pipeline(document_id: int, db: Session, current_user_id: Optional[int] = None):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        return

    doc.status = "PROCESSING"
    db.commit()

    # Read bytes
    with open(doc.file_path, "rb") as f:
        file_bytes = f.read()

    # 1. OCR Extraction
    ocr_result = await ocr_provider.extract_text_and_boxes(doc.file_path, file_bytes)
    doc.raw_ocr_text = ocr_result.raw_text
    doc.ocr_provider = ocr_result.provider_name

    # 2. AI Field Extraction & Confidence Scoring
    extracted_fields = field_extractor.extract_fields(ocr_result)

    # Clear old fields & validation results if reprocessing
    db.query(LandRecordField).filter(LandRecordField.document_id == doc.id).delete()
    db.query(ValidationResult).filter(ValidationResult.document_id == doc.id).delete()

    fields_dict = {}
    total_conf = 0.0
    field_objs = []
    for f in extracted_fields:
        fields_dict[f["field"]] = f["value"]
        total_conf += f["confidence"]
        field_obj = LandRecordField(
            document_id=doc.id,
            field_name=f["field"],
            extracted_value=f["value"],
            normalized_value=f["value"],
            confidence=f["confidence"],
            source_text=f["source_text"],
            bounding_box=f["bounding_box"],
            is_verified=False
        )
        db.add(field_obj)
        field_objs.append(field_obj)

    db.commit()

    overall_confidence = round(total_conf / len(extracted_fields), 2) if extracted_fields else 0.0

    # 3. Validation Engine
    val_engine = ValidationEngine(db)
    validation_results, requires_verification, is_disputed = val_engine.validate_fields(
        fields_dict=fields_dict,
        overall_confidence=overall_confidence
    )

    for vr in validation_results:
        db.add(ValidationResult(
            document_id=doc.id,
            rule_code=vr.rule_code,
            rule_name=vr.rule_name,
            severity=vr.severity,
            status=vr.status,
            target_field=vr.target_field,
            message=vr.message,
            details=vr.details
        ))

    # 4. Routing Decision (HITL or Auto-Promote)
    if requires_verification:
        doc.status = "REQUIRES_VERIFICATION"
        
        # Determine task priority
        priority = "HIGH" if (overall_confidence < 0.70 or is_disputed) else "MEDIUM"

        existing_task = db.query(VerificationTask).filter(VerificationTask.document_id == doc.id).first()
        if not existing_task:
            task = VerificationTask(
                document_id=doc.id,
                priority=priority,
                status="PENDING",
                notes="Automatic routing triggered by Validation Engine."
            )
            db.add(task)
        else:
            existing_task.priority = priority
            existing_task.status = "PENDING"

        AuditLogger.log_action(
            db=db,
            entity_name="document",
            entity_id=str(doc.id),
            action="ROUTED_TO_VERIFICATION",
            performed_by_id=current_user_id,
            new_values={"status": doc.status, "overall_confidence": overall_confidence, "is_disputed": is_disputed}
        )
    else:
        # High confidence and all rules passed -> Auto Verified
        doc.status = "VERIFIED"
        record_id_str = f"LR-{fields_dict.get('state', 'IN')[:2].upper()}-{fields_dict.get('district', 'DIS')[:2].upper()}-2026-{doc.id:05d}"
        
        # Promote to Land Record
        existing_record = db.query(LandRecord).filter(LandRecord.document_id == doc.id).first()
        if not existing_record:
            land_rec = LandRecord(
                document_id=doc.id,
                record_identifier=record_id_str,
                state=str(fields_dict.get("state", "Telangana")),
                district=str(fields_dict.get("district", "Ranga Reddy")),
                mandal_tehsil=str(fields_dict.get("mandal_tehsil", "Shamshabad")),
                village=str(fields_dict.get("village", "Mamidipally")),
                landowner_name=str(fields_dict.get("landowner_name", "Unknown")),
                survey_number=str(fields_dict.get("survey_number", "0")),
                khasra_number=fields_dict.get("khasra_number"),
                khata_number=fields_dict.get("khata_number"),
                plot_number=fields_dict.get("plot_number"),
                land_area=float(fields_dict.get("land_area", 1.0)),
                area_unit=str(fields_dict.get("area_unit", "Acres")),
                land_classification=str(fields_dict.get("land_classification", "Agricultural - Dry")),
                ownership_type=str(fields_dict.get("ownership_type", "Pattadar")),
                mutation_number=fields_dict.get("mutation_number"),
                registration_number=fields_dict.get("registration_number"),
                remarks=fields_dict.get("remarks"),
                overall_confidence=overall_confidence,
                is_verified=True,
                is_disputed=False,
                verified_at=datetime.now(timezone.utc)
            )
            db.add(land_rec)
            db.commit()
            db.refresh(land_rec)

            # Build GIS Parcel
            geom, c_lat, c_lng, area_sq_m = parcel_builder.build_parcel_geometry(
                survey_number=land_rec.survey_number,
                village=land_rec.village,
                land_area=land_rec.land_area,
                area_unit=land_rec.area_unit
            )
            db.add(GISParcel(
                land_record_id=land_rec.id,
                survey_number=land_rec.survey_number,
                village=land_rec.village,
                mandal_tehsil=land_rec.mandal_tehsil,
                district=land_rec.district,
                state=land_rec.state,
                center_latitude=c_lat,
                center_longitude=c_lng,
                geojson_geometry=geom,
                area_sq_meters=area_sq_m,
                status="VERIFIED"
            ))

        AuditLogger.log_action(
            db=db,
            entity_name="document",
            entity_id=str(doc.id),
            action="AUTO_VERIFIED",
            performed_by_id=current_user_id,
            new_values={"status": "VERIFIED", "overall_confidence": overall_confidence}
        )

    db.commit()


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("Pattadar Passbook / ROR"),
    allow_duplicate: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    file_size = len(contents)
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file_hash = calculate_sha256(contents)

    # Check exact duplicate document
    if not allow_duplicate:
        dupe_checker = DuplicateDetector(db)
        dupe_res = dupe_checker.check_duplicate_document(file_hash)
        if not dupe_res.passed:
            raise HTTPException(
                status_code=409,
                detail=dupe_res.message
            )
    else:
        # For testing/demo re-uploads, ensure unique hash for db constraint
        existing = db.query(Document).filter(Document.file_hash == file_hash).first()
        if existing:
            file_hash = f"{file_hash[:58]}_{uuid.uuid4().hex[:5]}"

    # Save to disk
    ext = os.path.splitext(file.filename)[1] or ".png"
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    saved_path = settings.UPLOADS_DIR / unique_filename

    with open(saved_path, "wb") as f:
        f.write(contents)

    doc = Document(
        file_name=file.filename,
        file_path=str(saved_path),
        file_hash=file_hash,
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/octet-stream",
        document_type=document_type,
        status="UPLOADED",
        uploaded_by_id=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    AuditLogger.log_action(
        db=db,
        entity_name="document",
        entity_id=str(doc.id),
        action="UPLOAD",
        performed_by_id=current_user.id,
        new_values={"file_name": doc.file_name, "file_size": file_size}
    )

    # Immediately execute document pipeline
    await process_document_pipeline(doc.id, db, current_user.id)
    db.refresh(doc)
    return doc


@router.get("", response_model=List[DocumentRead])
def list_documents(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    if status_filter:
        query = query.filter(Document.status == status_filter)
    return query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document_detail(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    fields = db.query(LandRecordField).filter(LandRecordField.document_id == doc.id).all()
    v_results = db.query(ValidationResult).filter(ValidationResult.document_id == doc.id).all()
    task = db.query(VerificationTask).filter(VerificationTask.document_id == doc.id).first()
    record = db.query(LandRecord).filter(LandRecord.document_id == doc.id).first()

    field_dtos = [
        ExtractedFieldDTO(
            field=f.field_name,
            value=f.verified_value if f.is_verified else f.extracted_value,
            confidence=f.confidence,
            source_text=f.source_text,
            verified=f.is_verified,
            bounding_box=f.bounding_box
        )
        for f in fields
    ]

    v_dtos = [
        ValidationResultDTO(
            id=vr.id,
            rule_code=vr.rule_code,
            rule_name=vr.rule_name,
            severity=vr.severity,
            status=vr.status,
            target_field=vr.target_field,
            message=vr.message,
            details=vr.details
        )
        for vr in v_results
    ]

    return DocumentDetail(
        id=doc.id,
        file_name=doc.file_name,
        file_path=doc.file_path,
        file_hash=doc.file_hash,
        file_size_bytes=doc.file_size_bytes,
        mime_type=doc.mime_type,
        document_type=doc.document_type,
        status=doc.status,
        ocr_provider=doc.ocr_provider,
        uploaded_by_id=doc.uploaded_by_id,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        raw_ocr_text=doc.raw_ocr_text,
        fields=field_dtos,
        validation_results=v_dtos,
        verification_task_id=task.id if task else None,
        land_record_id=record.id if record else None
    )


@router.post("/{document_id}/reprocess", response_model=DocumentDetail)
async def reprocess_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    await process_document_pipeline(doc.id, db, current_user.id)
    return get_document_detail(doc.id, db)
