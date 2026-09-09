from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db, get_current_user, require_roles
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.land_record import LandRecord
from backend.app.models.land_record_field import LandRecordField
from backend.app.models.validation_result import ValidationResult
from backend.app.models.verification_task import VerificationTask
from backend.app.models.gis_parcel import GISParcel
from backend.app.schemas.document import ExtractedFieldDTO, ValidationResultDTO
from backend.app.schemas.verification import (
    VerificationTaskRead, 
    VerificationStudioDetail, 
    FieldUpdatePayload, 
    BatchFieldUpdatePayload,
    VerificationDecision
)
from backend.app.services.validation.engine import ValidationEngine
from backend.app.services.gis.parcel_builder import CadastralParcelBuilder
from backend.app.services.audit.logger import AuditLogger

router = APIRouter()
parcel_builder = CadastralParcelBuilder()


@router.get("/tasks", response_model=List[VerificationTaskRead])
def list_verification_tasks(
    status_filter: Optional[str] = "PENDING",
    priority_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(VerificationTask)
    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(VerificationTask.status == status_filter.upper())
    if priority_filter:
        query = query.filter(VerificationTask.priority == priority_filter.upper())

    tasks = query.order_by(VerificationTask.created_at.desc()).all()
    results = []
    for t in tasks:
        doc = db.query(Document).filter(Document.id == t.document_id).first()
        fields = db.query(LandRecordField).filter(LandRecordField.document_id == t.document_id).all()
        f_dict = {f.field_name: (f.verified_value or f.extracted_value) for f in fields}
        avg_conf = sum(f.confidence for f in fields) / len(fields) if fields else 0.0

        results.append(VerificationTaskRead(
            id=t.id,
            document_id=t.document_id,
            priority=t.priority,
            status=t.status,
            assigned_to_id=t.assigned_to_id,
            rejection_reason=t.rejection_reason,
            notes=t.notes,
            created_at=t.created_at,
            resolved_at=t.resolved_at,
            file_name=doc.file_name if doc else "Document",
            village=f_dict.get("village"),
            survey_number=f_dict.get("survey_number"),
            overall_confidence=round(avg_conf, 2)
        ))
    return results


@router.get("/tasks/{task_id}", response_model=VerificationStudioDetail)
def get_verification_studio_detail(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(VerificationTask).filter(VerificationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Verification task not found")

    doc = db.query(Document).filter(Document.id == task.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Associated document not found")

    fields = db.query(LandRecordField).filter(LandRecordField.document_id == doc.id).all()
    v_results = db.query(ValidationResult).filter(ValidationResult.document_id == doc.id).all()

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

    f_dict = {f.field_name: (f.verified_value or f.extracted_value) for f in fields}
    avg_conf = sum(f.confidence for f in fields) / len(fields) if fields else 0.0

    task_read = VerificationTaskRead(
        id=task.id,
        document_id=task.document_id,
        priority=task.priority,
        status=task.status,
        assigned_to_id=task.assigned_to_id,
        rejection_reason=task.rejection_reason,
        notes=task.notes,
        created_at=task.created_at,
        resolved_at=task.resolved_at,
        file_name=doc.file_name,
        village=f_dict.get("village"),
        survey_number=f_dict.get("survey_number"),
        overall_confidence=round(avg_conf, 2)
    )

    return VerificationStudioDetail(
        task=task_read,
        document_id=doc.id,
        file_name=doc.file_name,
        file_path=doc.file_path,
        mime_type=doc.mime_type,
        raw_ocr_text=doc.raw_ocr_text,
        fields=field_dtos,
        validation_results=v_dtos
    )


@router.post("/tasks/{task_id}/field")
def update_single_field(
    task_id: int,
    payload: FieldUpdatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "verifier"))
):
    task = db.query(VerificationTask).filter(VerificationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Verification task not found")

    field_obj = db.query(LandRecordField).filter(
        LandRecordField.document_id == task.document_id,
        LandRecordField.field_name == payload.field_name
    ).first()

    if not field_obj:
        raise HTTPException(status_code=404, detail=f"Field {payload.field_name} not found")

    old_val = field_obj.verified_value or field_obj.extracted_value
    field_obj.verified_value = payload.value
    field_obj.is_verified = True
    field_obj.confidence = 1.0  # Verifier manually verified

    # Re-evaluate validation engine dynamically
    fields = db.query(LandRecordField).filter(LandRecordField.document_id == task.document_id).all()
    fields_dict = {f.field_name: (f.verified_value if f.is_verified else f.extracted_value) for f in fields}
    fields_dict[payload.field_name] = payload.value

    val_engine = ValidationEngine(db)
    results, requires_verif, is_disputed = val_engine.validate_fields(fields_dict, overall_confidence=0.95)

    # Refresh validation results
    db.query(ValidationResult).filter(ValidationResult.document_id == task.document_id).delete()
    for vr in results:
        db.add(ValidationResult(
            document_id=task.document_id,
            rule_code=vr.rule_code,
            rule_name=vr.rule_name,
            severity=vr.severity,
            status=vr.status,
            target_field=vr.target_field,
            message=vr.message,
            details=vr.details
        ))

    db.commit()

    AuditLogger.log_action(
        db=db,
        entity_name="land_record_field",
        entity_id=f"{task.document_id}:{payload.field_name}",
        action="EDIT_FIELD",
        performed_by_id=current_user.id,
        old_values={"value": old_val},
        new_values={"value": payload.value}
    )

    return {"message": "Field updated and live re-validated", "field": payload.field_name, "new_value": payload.value}


@router.post("/tasks/{task_id}/batch-fields")
def update_batch_fields(
    task_id: int,
    payload: BatchFieldUpdatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "verifier"))
):
    task = db.query(VerificationTask).filter(VerificationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Verification task not found")

    doc = db.query(Document).filter(Document.id == task.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Associated document not found")

    # Update all provided fields
    for field_name, val in payload.fields.items():
        field_obj = db.query(LandRecordField).filter(
            LandRecordField.document_id == task.document_id,
            LandRecordField.field_name == field_name
        ).first()
        if field_obj:
            field_obj.verified_value = val
            field_obj.is_verified = True
            field_obj.confidence = 1.0

    # Re-evaluate validation engine dynamically
    fields = db.query(LandRecordField).filter(LandRecordField.document_id == task.document_id).all()
    fields_dict = {f.field_name: (f.verified_value if f.is_verified else f.extracted_value) for f in fields}

    val_engine = ValidationEngine(db)
    results, requires_verif, is_disputed = val_engine.validate_fields(fields_dict, overall_confidence=0.95)

    # Refresh validation results
    db.query(ValidationResult).filter(ValidationResult.document_id == task.document_id).delete()
    for vr in results:
        db.add(ValidationResult(
            document_id=task.document_id,
            rule_code=vr.rule_code,
            rule_name=vr.rule_name,
            severity=vr.severity,
            status=vr.status,
            target_field=vr.target_field,
            message=vr.message,
            details=vr.details
        ))

    # Update task priority/notes if all rules pass
    failures = [r for r in results if r.status == "FAILED"]
    if not failures:
        task.priority = "LOW"
        task.notes = "All validation rules passed after verifier review."

    db.commit()

    AuditLogger.log_action(
        db=db,
        entity_name="verification_task",
        entity_id=str(task.id),
        action="EDIT_FIELDS_BATCH",
        performed_by_id=current_user.id,
        new_values=payload.fields
    )

    return {"message": "All fields updated and validation rules re-evaluated", "passed": len(failures) == 0, "failures_count": len(failures)}


@router.post("/tasks/{task_id}/decision")
def submit_verification_decision(
    task_id: int,
    decision: VerificationDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "verifier"))
):
    task = db.query(VerificationTask).filter(VerificationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Verification task not found")

    doc = db.query(Document).filter(Document.id == task.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Associated document not found")

    # If any batch field edits were provided in the payload
    if decision.edited_fields:
        for f_name, f_val in decision.edited_fields.items():
            f_obj = db.query(LandRecordField).filter(
                LandRecordField.document_id == doc.id,
                LandRecordField.field_name == f_name
            ).first()
            if f_obj:
                f_obj.verified_value = f_val
                f_obj.is_verified = True
                f_obj.confidence = 1.0

    task.notes = decision.notes
    task.resolved_at = datetime.now(timezone.utc)
    task.assigned_to_id = current_user.id

    if decision.decision.upper() == "APPROVE":
        task.status = "APPROVED"
        doc.status = "VERIFIED"

        # Extract verified values
        fields = db.query(LandRecordField).filter(LandRecordField.document_id == doc.id).all()
        f_dict = {f.field_name: (f.verified_value if f.is_verified else f.extracted_value) for f in fields}

        state_val = str(f_dict.get("state", "Telangana"))
        dist_val = str(f_dict.get("district", "Ranga Reddy"))
        surv_val = str(f_dict.get("survey_number", "100"))
        village_val = str(f_dict.get("village", "Mamidipally"))
        owner_val = str(f_dict.get("landowner_name", "Pattadar"))
        
        try:
            area_val = float(str(f_dict.get("land_area", "1.0")).replace(",", ""))
        except Exception:
            area_val = 1.0

        unit_val = str(f_dict.get("area_unit", "Acres"))
        record_id_str = f"LR-{state_val[:2].upper()}-{dist_val[:2].upper()}-2026-{doc.id:05d}"

        # Create or update official LandRecord
        existing_rec = db.query(LandRecord).filter(LandRecord.document_id == doc.id).first()
        if not existing_rec:
            land_rec = LandRecord(
                document_id=doc.id,
                record_identifier=record_id_str,
                state=state_val,
                district=dist_val,
                mandal_tehsil=str(f_dict.get("mandal_tehsil", "Shamshabad")),
                village=village_val,
                landowner_name=owner_val,
                survey_number=surv_val,
                khasra_number=f_dict.get("khasra_number"),
                khata_number=f_dict.get("khata_number"),
                plot_number=f_dict.get("plot_number"),
                land_area=area_val,
                area_unit=unit_val,
                land_classification=str(f_dict.get("land_classification", "Agricultural - Dry")),
                ownership_type=str(f_dict.get("ownership_type", "Pattadar")),
                mutation_number=f_dict.get("mutation_number"),
                registration_number=f_dict.get("registration_number"),
                remarks=f_dict.get("remarks"),
                overall_confidence=1.0,
                is_verified=True,
                is_disputed=False,
                verified_by_id=current_user.id,
                verified_at=datetime.now(timezone.utc)
            )
            db.add(land_rec)
            db.commit()
            db.refresh(land_rec)
        else:
            land_rec = existing_rec
            land_rec.state = state_val
            land_rec.district = dist_val
            land_rec.mandal_tehsil = str(f_dict.get("mandal_tehsil", "Shamshabad"))
            land_rec.village = village_val
            land_rec.landowner_name = owner_val
            land_rec.survey_number = surv_val
            land_rec.land_area = area_val
            land_rec.area_unit = unit_val
            land_rec.is_verified = True
            land_rec.overall_confidence = 1.0
            land_rec.verified_by_id = current_user.id
            land_rec.verified_at = datetime.now(timezone.utc)
            db.commit()

        # Build / Update GIS Cadastral Parcel
        existing_parcel = db.query(GISParcel).filter(GISParcel.land_record_id == land_rec.id).first()
        geom, c_lat, c_lng, area_sq_m = parcel_builder.build_parcel_geometry(
            survey_number=land_rec.survey_number,
            village=land_rec.village,
            land_area=land_rec.land_area,
            area_unit=land_rec.area_unit
        )
        if not existing_parcel:
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
        else:
            existing_parcel.survey_number = land_rec.survey_number
            existing_parcel.village = land_rec.village
            existing_parcel.center_latitude = c_lat
            existing_parcel.center_longitude = c_lng
            existing_parcel.geojson_geometry = geom
            existing_parcel.area_sq_meters = area_sq_m
            existing_parcel.status = "VERIFIED"

        AuditLogger.log_action(
            db=db,
            entity_name="verification_task",
            entity_id=str(task.id),
            action="APPROVE_RECORD",
            performed_by_id=current_user.id,
            new_values={"status": "APPROVED", "record_identifier": record_id_str, "survey_number": surv_val}
        )

        db.commit()
        return {"message": "Record approved and published to digital cadastre", "record_identifier": record_id_str}

    else:
        # Rejection
        task.status = "REJECTED"
        task.rejection_reason = decision.rejection_reason or "Document rejected by human verifier."
        doc.status = "REJECTED"

        AuditLogger.log_action(
            db=db,
            entity_name="verification_task",
            entity_id=str(task.id),
            action="REJECT_RECORD",
            performed_by_id=current_user.id,
            new_values={"status": "REJECTED", "reason": task.rejection_reason}
        )

        db.commit()
        return {"message": "Record marked as rejected", "reason": task.rejection_reason}
