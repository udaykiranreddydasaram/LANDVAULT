import os
from datetime import datetime, date, timezone
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.security import get_password_hash
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.land_record import LandRecord
from backend.app.models.land_record_field import LandRecordField
from backend.app.models.validation_result import ValidationResult
from backend.app.models.verification_task import VerificationTask
from backend.app.models.gis_parcel import GISParcel
from backend.app.models.audit_log import AuditLog
from backend.app.services.duplicate.detector import calculate_sha256
from backend.app.services.gis.parcel_builder import CadastralParcelBuilder

parcel_builder = CadastralParcelBuilder()


def create_sample_deed_image(filename: str, title: str, details: list) -> str:
    """Generates a realistic vintage government stamp paper image."""
    filepath = settings.SAMPLES_DIR / filename
    if filepath.exists():
        return str(filepath)

    # 800 x 1100 simulated legal sheet
    img = Image.new("RGB", (800, 1100), color=(252, 248, 238)) # Vintage yellowish parchment
    draw = ImageDraw.Draw(img)

    # Outer border (Legal stamp border)
    draw.rectangle([(30, 30), (770, 1070)], outline=(80, 50, 20), width=3)
    draw.rectangle([(38, 38), (762, 1062)], outline=(120, 90, 60), width=1)

    # Header Emblem box
    draw.rectangle([(250, 50), (550, 110)], outline=(140, 40, 40), width=2)
    draw.text((270, 65), "REVENUE DEPARTMENT", fill=(140, 40, 40))
    draw.text((260, 85), "GOVERNMENT LAND RECORD", fill=(50, 50, 50))

    # Title
    draw.text((70, 150), title, fill=(20, 20, 20))
    draw.line([(70, 175), (730, 175)], fill=(150, 150, 150), width=1)

    # Document details
    y = 210
    for line in details:
        if line.startswith("---"):
            draw.line([(70, y), (730, y)], fill=(180, 180, 180), width=1)
            y += 20
            continue
        draw.text((70, y), line, fill=(40, 40, 40))
        y += 35

    # Simulated official stamp / seal
    draw.ellipse([(580, 850), (720, 990)], outline=(180, 30, 30), width=3)
    draw.text((605, 910), "TAHSILDAR", fill=(180, 30, 30))
    draw.text((615, 930), "SEAL & SIGN", fill=(180, 30, 30))

    img.save(filepath)
    return str(filepath)


def seed_database_if_empty(db: Session):
    if db.query(User).count() > 0:
        return

    print("Initializing LANDVAULT AI Demo Seeds...")

    # 1. Seed Users
    admin = User(
        username="admin",
        email="admin@landvault.gov.in",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Dr. Rameshwar Rao, IAS",
        role="admin",
        department="Directorate of Land Records & Survey"
    )
    verifier = User(
        username="verifier",
        email="verifier@landvault.gov.in",
        hashed_password=get_password_hash("verifierpassword123"),
        full_name="Smt. Shailaja Sharma",
        role="verifier",
        department="Tahsildar & Revenue Verification Division"
    )
    viewer = User(
        username="viewer",
        email="viewer@landvault.gov.in",
        hashed_password=get_password_hash("viewerpassword123"),
        full_name="Citizen / Bank Audit Officer",
        role="viewer",
        department="Public Registry & Legal Verification"
    )
    db.add_all([admin, verifier, viewer])
    db.commit()
    db.refresh(admin)
    db.refresh(verifier)

    # 2. Create sample images
    clean_deed_path = create_sample_deed_image(
        "Sample_Patta_Deed_Telangana_Clean.png",
        "RECORD OF RIGHTS (ROR) / PATTADAR PASSBOOK",
        [
            "State: Telangana | District: Ranga Reddy",
            "Mandal: Shamshabad | Village: Mamidipally",
            "Pattadar Name: Smt. Anasuya Devi",
            "Survey Number: 148/2",
            "Khasra Number: 148/A | Khata Number: 512 | Plot No: PL-08",
            "Land Area Extent: 3.20 Acres",
            "Land Classification: Agricultural - Dry (Patta)",
            "Ownership Type: Pattadar",
            "Mutation Order No: MUT-2021-00452",
            "Registration No: 7812/2005",
            "Registration Date: 2005-04-12",
            "---",
            "Certified non-assigned private patta holding."
        ]
    )

    smudged_deed_path = create_sample_deed_image(
        "Sample_Patta_Deed_Telangana_Smudged_1988.png",
        "CERTIFIED EXTRACT - REVENUE DEED (1988)",
        [
            "State: Telangana | District: Ranga Reddy",
            "Mandal: Shamshabad | Village: Mamidipally",
            "Pattadar / Landowner Name: Sri K. Venkat Reddy",
            "Survey No: 124/?  [*** INK SMUDGE ON PHYSICAL DEED ***]",
            "Khasra No: 124/KH-4 | Khata No: 408 | Plot No: P-12",
            "Extent / Land Area: 2.45 Acres",
            "Classification: Agricultural - Dry",
            "Ownership Type: Pattadar",
            "Mutation Order No: MUT-2018-09823",
            "Registration No: 4521/1988",
            "Registration Date: 1988-10-14",
            "---",
            "Ancestral partition deed. Original paper stamped at Shamshabad."
        ]
    )

    pune_deed_path = create_sample_deed_image(
        "Sample_7_12_Extract_Maharashtra.png",
        "GOVERNMENT OF MAHARASHTRA - FORM VII-XII",
        [
            "State: Maharashtra | District: Pune",
            "Tehsil: Haveli | Village: Wagholi",
            "Landowner / Bhogvatdar: Rajeshwar Dattatray Patil",
            "Survey / Gat Number: 88/1A",
            "Khata Number: 184",
            "Total Land Area: 1.75 Hectares",
            "Land Classification: Jirayat (Agricultural)",
            "Ownership Type: Sole Proprietor (Class 1)",
            "Mutation No: MUT-MH-2019-112",
            "Registration No: 2014-9981",
            "Registration Date: 2014-06-20",
            "---",
            "Verified digital extract from Mahabhulekh cadastre."
        ]
    )

    # 3. Seed Document 1: Clean Verified Document (Telangana)
    with open(clean_deed_path, "rb") as f:
        c_bytes = f.read()
    doc1 = Document(
        file_name="Sample_Patta_Deed_Telangana_Clean.png",
        file_path=clean_deed_path,
        file_hash=calculate_sha256(c_bytes),
        file_size_bytes=len(c_bytes),
        mime_type="image/png",
        document_type="Pattadar Passbook / ROR",
        status="VERIFIED",
        ocr_provider="MockSmartOCR-CleanScan",
        uploaded_by_id=admin.id
    )
    db.add(doc1)
    db.commit()
    db.refresh(doc1)

    rec1 = LandRecord(
        document_id=doc1.id,
        record_identifier="LR-TS-RR-2026-00001",
        state="Telangana",
        district="Ranga Reddy",
        mandal_tehsil="Shamshabad",
        village="Mamidipally",
        landowner_name="Smt. Anasuya Devi",
        survey_number="148/2",
        khasra_number="148/A",
        khata_number="512",
        plot_number="PL-08",
        land_area=3.20,
        area_unit="Acres",
        land_classification="Agricultural - Dry",
        ownership_type="Pattadar",
        mutation_number="MUT-2021-00452",
        registration_number="7812/2005",
        registration_date=date(2005, 4, 12),
        overall_confidence=0.97,
        is_verified=True,
        is_disputed=False,
        verified_by_id=admin.id,
        verified_at=datetime.now(timezone.utc)
    )
    db.add(rec1)
    db.commit()
    db.refresh(rec1)

    g1, c1_lat, c1_lng, a1 = parcel_builder.build_parcel_geometry("148/2", "Mamidipally", 3.20, "Acres")
    db.add(GISParcel(
        land_record_id=rec1.id,
        survey_number="148/2",
        village="Mamidipally",
        mandal_tehsil="Shamshabad",
        district="Ranga Reddy",
        state="Telangana",
        center_latitude=c1_lat,
        center_longitude=c1_lng,
        geojson_geometry=g1,
        area_sq_meters=a1,
        status="VERIFIED"
    ))

    # 4. Seed Document 2: Pune Maharashtra Verified Record
    with open(pune_deed_path, "rb") as f:
        p_bytes = f.read()
    doc2 = Document(
        file_name="Sample_7_12_Extract_Maharashtra.png",
        file_path=pune_deed_path,
        file_hash=calculate_sha256(p_bytes),
        file_size_bytes=len(p_bytes),
        mime_type="image/png",
        document_type="7/12 Extract",
        status="VERIFIED",
        ocr_provider="MockSmartOCR-Mahabhulekh",
        uploaded_by_id=admin.id
    )
    db.add(doc2)
    db.commit()
    db.refresh(doc2)

    rec2 = LandRecord(
        document_id=doc2.id,
        record_identifier="LR-MH-PU-2026-00002",
        state="Maharashtra",
        district="Pune",
        mandal_tehsil="Haveli",
        village="Wagholi",
        landowner_name="Rajeshwar Dattatray Patil",
        survey_number="88/1A",
        khata_number="184",
        land_area=1.75,
        area_unit="Hectares",
        land_classification="Agricultural - Jirayat",
        ownership_type="Sole Proprietor (Class 1)",
        mutation_number="MUT-MH-2019-112",
        registration_number="2014-9981",
        registration_date=date(2014, 6, 20),
        overall_confidence=0.96,
        is_verified=True,
        is_disputed=False,
        verified_by_id=admin.id,
        verified_at=datetime.now(timezone.utc)
    )
    db.add(rec2)
    db.commit()
    db.refresh(rec2)

    g2, c2_lat, c2_lng, a2 = parcel_builder.build_parcel_geometry("88/1A", "Wagholi", 1.75, "Hectares")
    db.add(GISParcel(
        land_record_id=rec2.id,
        survey_number="88/1A",
        village="Wagholi",
        mandal_tehsil="Haveli",
        district="Pune",
        state="Maharashtra",
        center_latitude=c2_lat,
        center_longitude=c2_lng,
        geojson_geometry=g2,
        area_sq_meters=a2,
        status="VERIFIED"
    ))

    # 5. Seed Document 3: Smudged Deed routed to Human Verification Queue
    with open(smudged_deed_path, "rb") as f:
        s_bytes = f.read()
    doc3 = Document(
        file_name="Sample_Patta_Deed_Telangana_Smudged_1988.png",
        file_path=smudged_deed_path,
        file_hash=calculate_sha256(s_bytes),
        file_size_bytes=len(s_bytes),
        mime_type="image/png",
        document_type="Pattadar Passbook / ROR",
        status="REQUIRES_VERIFICATION",
        ocr_provider="MockSmartOCR-HighResSimulator",
        uploaded_by_id=verifier.id
    )
    db.add(doc3)
    db.commit()
    db.refresh(doc3)

    # Extracted fields for the smudged deed
    fields_data = [
        ("state", "Telangana", 0.96, "State: Telangana", {"x": 10, "y": 12, "w": 30, "h": 3, "page": 1}),
        ("district", "Ranga Reddy", 0.95, "District: Ranga Reddy", {"x": 10, "y": 16, "w": 35, "h": 3, "page": 1}),
        ("mandal_tehsil", "Shamshabad", 0.94, "Mandal: Shamshabad", {"x": 10, "y": 20, "w": 35, "h": 3, "page": 1}),
        ("village", "Mamidipally", 0.96, "Village: Mamidipally", {"x": 10, "y": 24, "w": 35, "h": 3, "page": 1}),
        ("landowner_name", "Sri K. Venkat Reddy", 0.92, "Landowner: Sri K. Venkat Reddy", {"x": 10, "y": 30, "w": 45, "h": 4, "page": 1}),
        # LOW CONFIDENCE FIELD!
        ("survey_number", "124/?", 0.54, "Survey No: 124/? (Ink smudge)", {"x": 10, "y": 36, "w": 32, "h": 4, "page": 1}),
        ("khasra_number", "124/KH-4", 0.88, "Khasra No: 124/KH-4", {"x": 50, "y": 36, "w": 35, "h": 4, "page": 1}),
        ("khata_number", "408", 0.91, "Khata No: 408", {"x": 10, "y": 42, "w": 25, "h": 3, "page": 1}),
        ("plot_number", "P-12", 0.89, "Plot No: P-12", {"x": 50, "y": 42, "w": 25, "h": 3, "page": 1}),
        ("land_area", "2.45", 0.94, "Land Area: 2.45 Acres", {"x": 10, "y": 48, "w": 38, "h": 3, "page": 1}),
        ("area_unit", "Acres", 0.96, "Acres", {"x": 35, "y": 48, "w": 12, "h": 3, "page": 1}),
        ("land_classification", "Agricultural - Dry", 0.93, "Classification: Agricultural - Dry", {"x": 10, "y": 54, "w": 50, "h": 3, "page": 1}),
        ("ownership_type", "Pattadar", 0.95, "Ownership Type: Pattadar", {"x": 10, "y": 60, "w": 40, "h": 3, "page": 1}),
        ("mutation_number", "MUT-2018-09823", 0.89, "Mutation No: MUT-2018-09823", {"x": 10, "y": 66, "w": 45, "h": 3, "page": 1}),
        ("registration_number", "4521/1988", 0.91, "Registration No: 4521/1988", {"x": 10, "y": 72, "w": 42, "h": 3, "page": 1}),
        ("registration_date", "1988-10-14", 0.90, "Registration Date: 1988-10-14", {"x": 10, "y": 78, "w": 45, "h": 3, "page": 1}),
    ]

    for fn, fv, fc, fs, fb in fields_data:
        db.add(LandRecordField(
            document_id=doc3.id,
            field_name=fn,
            extracted_value=fv,
            normalized_value=fv,
            confidence=fc,
            source_text=fs,
            bounding_box=fb,
            is_verified=False
        ))

    # Add validation failures for the smudged deed
    db.add(ValidationResult(
        document_id=doc3.id,
        rule_code="VAL_SURVEY_FMT",
        rule_name="Survey Number Format",
        severity="ERROR",
        status="FAILED",
        target_field="survey_number",
        message="Survey number '124/?' contains unreadable characters or ink smudge placeholders.",
        details={"raw_value": "124/?"}
    ))
    db.add(ValidationResult(
        document_id=doc3.id,
        rule_code="VAL_CONFIDENCE_THRESHOLD",
        rule_name="AI Confidence Threshold Evaluation",
        severity="WARNING",
        status="FAILED",
        target_field="survey_number",
        message="Survey Number confidence score is 54% (below 70% threshold).",
        details={"confidence": 0.54}
    ))

    # Verification task
    db.add(VerificationTask(
        document_id=doc3.id,
        priority="HIGH",
        status="PENDING",
        notes="Ink smudge detected on physical deed at Survey Number. Requires human officer confirmation."
    ))

    # 6. Seed a Disputed Record (Collision Demo)
    disp_deed_path = create_sample_deed_image(
        "Sample_Deed_Conflicting_Claimant.png",
        "REVENUE DEED - CLAIMANT SUBMISSION",
        [
            "State: Telangana | District: Ranga Reddy",
            "Mandal: Shamshabad | Village: Mamidipally",
            "Claimant Name: Sri G. Chandrasekhar",
            "Survey Number: 148/2",
            "Land Area Extent: 3.20 Acres",
            "Land Classification: Agricultural - Dry",
            "---",
            "Disputed overlapping claim with primary title."
        ]
    )
    with open(disp_deed_path, "rb") as f:
        d_bytes = f.read()

    doc_disp = Document(
        file_name="Sample_Deed_Conflicting_Claimant.png",
        file_path=disp_deed_path,
        file_hash=calculate_sha256(d_bytes),
        file_size_bytes=len(d_bytes),
        mime_type="image/png",
        document_type="Disputed Claim Affidavit",
        status="REQUIRES_VERIFICATION",
        ocr_provider="MockSmartOCR-HighResSimulator",
        uploaded_by_id=admin.id
    )
    db.add(doc_disp)
    db.commit()
    db.refresh(doc_disp)

    rec_disp = LandRecord(
        document_id=doc_disp.id,
        record_identifier="LR-TS-RR-2026-DISP01",
        state="Telangana",
        district="Ranga Reddy",
        mandal_tehsil="Shamshabad",
        village="Mamidipally",
        landowner_name="Sri G. Chandrasekhar (Conflicting Claimant)",
        survey_number="148/2",
        land_area=3.20,
        area_unit="Acres",
        overall_confidence=0.82,
        is_verified=False,
        is_disputed=True,
        remarks="Flagged by Cadastral Collision Detector: Survey 148/2 overlapping claim with Smt. Anasuya Devi."
    )
    db.add(rec_disp)
    db.commit()
    db.refresh(rec_disp)

    g_disp, cd_lat, cd_lng, a_disp = parcel_builder.build_parcel_geometry("148/2-B", "Mamidipally", 3.20, "Acres")
    db.add(GISParcel(
        land_record_id=rec_disp.id,
        survey_number="148/2",
        village="Mamidipally",
        mandal_tehsil="Shamshabad",
        district="Ranga Reddy",
        state="Telangana",
        center_latitude=cd_lat,
        center_longitude=cd_lng,
        geojson_geometry=g_disp,
        area_sq_meters=a_disp,
        status="DISPUTED"
    ))

    # Seed Initial Audit Log
    AuditLogEntry = AuditLog(
        entity_name="system",
        entity_id="INIT-SEED",
        action="SYSTEM_INITIALIZATION",
        performed_by_id=admin.id,
        new_values={"seeded_records": 4, "demo_mode": True},
        ip_address="127.0.0.1"
    )
    db.add(AuditLogEntry)

    db.commit()
    print("LANDVAULT AI Demo Seeds successfully initialized!")
