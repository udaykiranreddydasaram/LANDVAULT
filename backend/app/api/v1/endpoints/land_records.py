from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db, get_current_user
from backend.app.models.land_record import LandRecord
from backend.app.models.document import Document
from backend.app.models.user import User
from backend.app.schemas.land_record import LandRecordRead

router = APIRouter()


@router.get("", response_model=List[LandRecordRead])
def list_land_records(
    search: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    village: Optional[str] = None,
    is_verified: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(LandRecord)
    if is_verified is not None:
        query = query.filter(LandRecord.is_verified == is_verified)
    if state:
        query = query.filter(LandRecord.state.ilike(f"%{state}%"))
    if district:
        query = query.filter(LandRecord.district.ilike(f"%{district}%"))
    if village:
        query = query.filter(LandRecord.village.ilike(f"%{village}%"))
    if search:
        s = f"%{search}%"
        query = query.filter(
            (LandRecord.landowner_name.ilike(s)) |
            (LandRecord.survey_number.ilike(s)) |
            (LandRecord.record_identifier.ilike(s)) |
            (LandRecord.village.ilike(s))
        )
    return query.order_by(LandRecord.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/{record_id}", response_model=LandRecordRead)
def get_land_record_detail(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(LandRecord).filter(LandRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Land record not found")
    return rec


@router.get("/{record_id}/certificate")
def get_land_record_certificate(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(LandRecord).filter(LandRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Land record not found")

    doc = db.query(Document).filter(Document.id == rec.document_id).first()
    verifier = db.query(User).filter(User.id == rec.verified_by_id).first() if rec.verified_by_id else None

    return {
        "certificate_id": f"CERT-{rec.record_identifier}",
        "record_identifier": rec.record_identifier,
        "state": rec.state,
        "district": rec.district,
        "mandal_tehsil": rec.mandal_tehsil,
        "village": rec.village,
        "landowner_name": rec.landowner_name,
        "survey_number": rec.survey_number,
        "khasra_number": rec.khasra_number,
        "khata_number": rec.khata_number,
        "plot_number": rec.plot_number,
        "land_area": rec.land_area,
        "area_unit": rec.area_unit,
        "land_classification": rec.land_classification,
        "ownership_type": rec.ownership_type,
        "mutation_number": rec.mutation_number,
        "registration_number": rec.registration_number,
        "registration_date": str(rec.registration_date) if rec.registration_date else None,
        "is_verified": rec.is_verified,
        "is_disputed": rec.is_disputed,
        "verified_by": verifier.full_name if verifier else "System Auto-Verification",
        "verified_at": str(rec.verified_at) if rec.verified_at else None,
        "original_document_hash": doc.file_hash if doc else None,
        "security_seal": "DIGITALLY_SEALED_BY_LANDVAULT_AI",
        "timestamp": str(rec.updated_at)
    }
