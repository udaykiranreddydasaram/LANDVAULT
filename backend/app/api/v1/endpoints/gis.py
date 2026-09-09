from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.models.gis_parcel import GISParcel
from backend.app.models.land_record import LandRecord
from backend.app.schemas.gis import GeoJSONFeatureCollection, GeoJSONFeature, GISParcelProperties

router = APIRouter()


@router.get("/parcels", response_model=GeoJSONFeatureCollection)
def get_all_cadastral_parcels(
    village: Optional[str] = None,
    district: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(GISParcel)
    if village:
        query = query.filter(GISParcel.village.ilike(f"%{village}%"))
    if district:
        query = query.filter(GISParcel.district.ilike(f"%{district}%"))
    if status_filter:
        query = query.filter(GISParcel.status == status_filter.upper())

    parcels = query.all()
    features = []

    for p in parcels:
        rec = db.query(LandRecord).filter(LandRecord.id == p.land_record_id).first()
        props = GISParcelProperties(
            id=p.id,
            land_record_id=p.land_record_id,
            survey_number=p.survey_number,
            village=p.village,
            mandal_tehsil=p.mandal_tehsil,
            district=p.district,
            state=p.state,
            landowner_name=rec.landowner_name if rec else None,
            land_area=rec.land_area if rec else None,
            area_unit=rec.area_unit if rec else "Acres",
            khata_number=rec.khata_number if rec else None,
            status=p.status,
            overall_confidence=rec.overall_confidence if rec else 1.0
        )
        features.append(GeoJSONFeature(
            type="Feature",
            id=p.id,
            geometry=p.geojson_geometry,
            properties=props
        ))

    return GeoJSONFeatureCollection(
        type="FeatureCollection",
        features=features
    )


@router.get("/parcels/{parcel_id}", response_model=GeoJSONFeature)
def get_single_parcel(parcel_id: int, db: Session = Depends(get_db)):
    p = db.query(GISParcel).filter(GISParcel.id == parcel_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Cadastral parcel not found")

    rec = db.query(LandRecord).filter(LandRecord.id == p.land_record_id).first()
    props = GISParcelProperties(
        id=p.id,
        land_record_id=p.land_record_id,
        survey_number=p.survey_number,
        village=p.village,
        mandal_tehsil=p.mandal_tehsil,
        district=p.district,
        state=p.state,
        landowner_name=rec.landowner_name if rec else None,
        land_area=rec.land_area if rec else None,
        area_unit=rec.area_unit if rec else "Acres",
        khata_number=rec.khata_number if rec else None,
        status=p.status,
        overall_confidence=rec.overall_confidence if rec else 1.0
    )
    return GeoJSONFeature(
        type="Feature",
        id=p.id,
        geometry=p.geojson_geometry,
        properties=props
    )
