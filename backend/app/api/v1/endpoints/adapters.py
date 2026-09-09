from fastapi import APIRouter
from backend.app.adapters.dilrmp_mock import dilrmp_adapter
from backend.app.adapters.lrms_mock import lrms_adapter

router = APIRouter()


@router.get("/dilrmp/verify/{survey_number}")
async def verify_dilrmp_cadastral(
    survey_number: str,
    village: str = "Mamidipally",
    district: str = "Ranga Reddy",
    state: str = "Telangana"
):
    return await dilrmp_adapter.verify_cadastral_alignment(
        survey_number=survey_number,
        village=village,
        district=district,
        state=state
    )


@router.post("/lrms/sync-mutation")
async def sync_lrms_mutation(
    record_identifier: str = "LR-TS-RR-2026-00001",
    landowner_name: str = "Sri K. Venkat Reddy",
    survey_number: str = "124/2",
    land_area: float = 2.45,
    area_unit: str = "Acres"
):
    return await lrms_adapter.sync_mutation_record(
        record_identifier=record_identifier,
        landowner_name=landowner_name,
        survey_number=survey_number,
        land_area=land_area,
        area_unit=area_unit
    )
