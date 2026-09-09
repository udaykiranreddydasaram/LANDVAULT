from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    auth,
    documents,
    verification,
    land_records,
    gis,
    analytics,
    audit,
    adapters
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & RBAC"])
api_router.include_router(documents.router, prefix="/documents", tags=["Document Processing & OCR"])
api_router.include_router(verification.router, prefix="/verification", tags=["Human Verification Studio"])
api_router.include_router(land_records.router, prefix="/land-records", tags=["Land Records Registry"])
api_router.include_router(gis.router, prefix="/gis", tags=["GIS & Cadastral Mapping"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & KPIs"])
api_router.include_router(audit.router, prefix="/audit", tags=["Tamper-Evident Audit Trail"])
api_router.include_router(adapters.router, prefix="/adapters", tags=["Government Mock Adapters"])
