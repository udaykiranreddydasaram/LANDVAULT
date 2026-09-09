from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class GeoJSONGeometry(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]


class GISParcelProperties(BaseModel):
    id: int
    land_record_id: int
    survey_number: str
    village: str
    mandal_tehsil: Optional[str] = None
    district: str
    state: str
    landowner_name: Optional[str] = None
    land_area: Optional[float] = None
    area_unit: Optional[str] = "Acres"
    khata_number: Optional[str] = None
    status: str
    overall_confidence: Optional[float] = None


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    id: int
    geometry: Dict[str, Any]
    properties: GISParcelProperties


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
