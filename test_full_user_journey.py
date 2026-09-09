"""
Complete End-to-End User Journey QA Test Suite for LANDVAULT AI
Tests all 23 steps required for SIH judging demonstration.
"""
import os
import sys
import time
import requests

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_API = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:5173"

def run_test():
    print("=" * 70)
    print("LANDVAULT AI — 23-Step Automated End-to-End User Journey Verification")
    print("=" * 70)

    # STEP 1 & 2: Login Page & Login as Verifier
    print("\n[Step 1 & 2] Authenticating as Verifier...")
    login_res = requests.post(
        f"{BASE_API}/auth/login-json",
        json={"username": "verifier", "password": "verifierpassword123"}
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    auth_data = login_res.json()
    token = auth_data["access_token"]
    user = auth_data["user"]
    print(f"  ✓ Logged in as: {user['username']} ({user['full_name']}) - Role: {user['role']}")
    headers = {"Authorization": f"Bearer {token}"}

    # Verify user profile
    me_res = requests.get(f"{BASE_API}/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["role"] == "verifier"

    # STEP 3: Open Dashboard
    print("\n[Step 3] Fetching Dashboard Metrics...")
    dash_res = requests.get(f"{BASE_API}/analytics/dashboard", headers=headers)
    assert dash_res.status_code == 200, f"Dashboard failed: {dash_res.text}"
    dash_data = dash_res.json()
    initial_verified = dash_data["metrics"]["verified_records"]
    initial_pending = dash_data["metrics"]["pending_verification"]
    print(f"  ✓ Dashboard metrics loaded: Verified={initial_verified}, Pending={initial_pending}, Total={dash_data['metrics']['total_documents']}")

    # STEP 4: Open Documents
    print("\n[Step 4] Opening Documents Vault...")
    docs_res = requests.get(f"{BASE_API}/documents", headers=headers)
    assert docs_res.status_code == 200
    docs = docs_res.json()
    print(f"  ✓ Documents vault loaded: {len(docs)} documents listed")

    # STEP 5 & 6: Upload synthetic land-record document & start processing
    print("\n[Step 5 & 6] Uploading & Ingesting Smudged Patta Deed (1988)...")
    sample_file = "c:/Users/udayk/Documents/antigravity/backend/samples/Sample_Patta_Deed_Telangana_Smudged_1988.png"
    assert os.path.exists(sample_file), f"Sample file not found at {sample_file}"
    
    with open(sample_file, "rb") as f:
        upload_res = requests.post(
            f"{BASE_API}/documents/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (f"QA_Run_Deed_{int(time.time())}.png", f, "image/png")},
            data={"document_type": "Pattadar Passbook / ROR", "allow_duplicate": "true"}
        )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    uploaded_doc = upload_res.json()
    doc_id = uploaded_doc["id"]
    print(f"  ✓ Ingestion pipeline executed: Doc ID={doc_id}, Status={uploaded_doc['status']}")

    # STEP 7: Verify OCR & Extraction Results
    print("\n[Step 7] Verifying OCR & Field Extraction...")
    doc_detail_res = requests.get(f"{BASE_API}/documents/{doc_id}", headers=headers)
    assert doc_detail_res.status_code == 200
    doc_detail = doc_detail_res.json()
    fields = doc_detail["fields"]
    assert len(fields) >= 10, f"Expected >= 10 extracted fields, got {len(fields)}"
    field_map = {f["field"]: f for f in fields}
    print(f"  ✓ {len(fields)} cadastral fields extracted by {doc_detail['ocr_provider']}")
    print(f"    - Survey Number raw: '{field_map.get('survey_number', {}).get('value')}'")
    print(f"    - Landowner Name: '{field_map.get('landowner_name', {}).get('value')}'")
    print(f"    - Village: '{field_map.get('village', {}).get('value')}'")

    # STEP 8: Verify Confidence Scores
    print("\n[Step 8] Verifying Tri-Factor Confidence Scores...")
    survey_conf = field_map.get("survey_number", {}).get("confidence", 1.0)
    print(f"  ✓ Survey Number Confidence: {round(survey_conf * 100)}% (Smudged detection)")
    assert survey_conf < 0.70, f"Expected low confidence for smudged field, got {survey_conf}"

    # STEP 9: Verify Validation Results
    print("\n[Step 9] Verifying Validation Rule Engine Results...")
    val_results = doc_detail["validation_results"]
    assert len(val_results) > 0, "No validation results returned"
    failed_rules = [vr for vr in val_results if vr["status"] == "FAILED"]
    print(f"  ✓ Validation engine executed {len(val_results)} rules:")
    for vr in val_results:
        print(f"    [{vr['status']}] {vr['rule_code']}: {vr['message']}")
    assert len(failed_rules) > 0, "Expected validation failure for smudged survey number"

    # STEP 10: Open Verification Queue
    print("\n[Step 10] Opening Human Verification Queue...")
    tasks_res = requests.get(f"{BASE_API}/verification/tasks?status_filter=ALL", headers=headers)
    assert tasks_res.status_code == 200
    all_tasks = tasks_res.json()
    matching_task = next((t for t in all_tasks if t["document_id"] == doc_id), None)
    assert matching_task is not None, f"No verification task found for document {doc_id}"
    task_id = matching_task["id"]
    print(f"  ✓ Task #{task_id} present in queue: Priority={matching_task['priority']}, Status={matching_task['status']}")

    # STEP 11 & 12: Open Verification Studio & check split-screen data
    print("\n[Step 11 & 12] Loading Split-Screen Verification Studio...")
    studio_res = requests.get(f"{BASE_API}/verification/tasks/{task_id}", headers=headers)
    assert studio_res.status_code == 200
    studio_data = studio_res.json()
    assert len(studio_data["fields"]) > 0
    assert any(f.get("bounding_box") is not None for f in studio_data["fields"]), "Bounding boxes missing"
    print(f"  ✓ Studio loaded: {len(studio_data['fields'])} fields with SVG bounding boxes synchronized")

    # STEP 13 & 14: Edit low-confidence field & re-run validation
    print("\n[Step 13 & 14] Editing Low-Confidence Survey Number (124/? -> 124/2) & Re-running Validation...")
    # Update field
    edit_res = requests.post(
        f"{BASE_API}/verification/tasks/{task_id}/batch-fields",
        headers=headers,
        json={"fields": {"survey_number": "124/2"}}
    )
    assert edit_res.status_code == 200, f"Batch update failed: {edit_res.text}"
    assert edit_res.json()["passed"] is True, f"Validation rules should now pass! Result: {edit_res.json()}"
    print(f"  ✓ Field updated and re-validated: {edit_res.json()['message']}")

    # Verify updated studio detail has no failures
    studio_refreshed = requests.get(f"{BASE_API}/verification/tasks/{task_id}", headers=headers).json()
    fresh_failures = [vr for vr in studio_refreshed["validation_results"] if vr["status"] == "FAILED"]
    assert len(fresh_failures) == 0, f"Remaining failures: {fresh_failures}"
    print("  ✓ All 6 validation rules are now PASSED")

    # STEP 15: Approve Record
    print("\n[Step 15] Verifier Approves Record...")
    approve_res = requests.post(
        f"{BASE_API}/verification/tasks/{task_id}/decision",
        headers=headers,
        json={
            "decision": "APPROVE",
            "notes": "Verified against physical 1988 stamp paper. Survey 124/2 confirmed.",
            "edited_fields": {"survey_number": "124/2"}
        }
    )
    assert approve_res.status_code == 200, f"Approval failed: {approve_res.text}"
    approval_data = approve_res.json()
    rec_id_str = approval_data["record_identifier"]
    print(f"  ✓ Record officially approved! Identifier: {rec_id_str}")

    # STEP 16 & 17: Open Land Records & Search
    print("\n[Step 16 & 17] Searching Land Records Registry...")
    records_res = requests.get(f"{BASE_API}/land-records", headers=headers)
    assert records_res.status_code == 200
    records = records_res.json()
    matching_rec = next((r for r in records if r["record_identifier"] == rec_id_str or r["survey_number"] == "124/2"), None)
    assert matching_rec is not None, f"Approved record {rec_id_str} not found in registry"
    land_rec_id = matching_rec["id"]
    print(f"  ✓ Record #{land_rec_id} found in Registry: Owner='{matching_rec['landowner_name']}', Survey={matching_rec['survey_number']}")

    # STEP 18: Record Details & Certificate
    print("\n[Step 18] Inspecting Official Digital Title Certificate...")
    cert_res = requests.get(f"{BASE_API}/land-records/{land_rec_id}/certificate", headers=headers)
    assert cert_res.status_code == 200
    cert = cert_res.json()
    assert "ulpin" in cert, "Certificate missing ULPIN"
    print(f"  ✓ Official Certificate Generated:")
    print(f"    - Title Certificate No: {cert['certificate_number']}")
    print(f"    - ULPIN: {cert['ulpin']}")
    print(f"    - Legal Status: {cert['legal_status']}")

    # STEP 19: Check Audit Trail
    print("\n[Step 19] Checking Immutable Compliance Audit Trail...")
    audit_res = requests.get(f"{BASE_API}/audit/logs", headers=headers)
    assert audit_res.status_code == 200
    audit_logs = audit_res.json()
    recent_actions = [l["action"] for l in audit_logs[:5]]
    print(f"  ✓ Recent audit actions recorded: {recent_actions}")
    assert any("APPROVE_RECORD" in a or "EDIT" in a for a in recent_actions), "Expected audit action not recorded"

    # STEP 20 & 21: Open GIS Map & Click Parcel
    print("\n[Step 20 & 21] Verifying Cadastral GIS Parcel on Map...")
    gis_res = requests.get(f"{BASE_API}/gis/parcels", headers=headers)
    assert gis_res.status_code == 200
    geojson = gis_res.json()
    matching_parcel = next((f for f in geojson["features"] if f["properties"]["survey_number"] == "124/2"), None)
    assert matching_parcel is not None, "Cadastral parcel for survey 124/2 was not synthesized"
    p_props = matching_parcel["properties"]
    print(f"  ✓ Cadastral Parcel confirmed on GIS Map:")
    print(f"    - Survey: {p_props['survey_number']} ({p_props['status']})")
    print(f"    - Center: Lat {p_props['center_latitude']}, Lng {p_props['center_longitude']}")
    print(f"    - Polygon Vertices: {len(matching_parcel['geometry']['coordinates'][0])} coordinates")
    print(f"    - Linked Record ID: {p_props['land_record_id']}")
    assert p_props["land_record_id"] == land_rec_id, "Parcel not linked to the correct land record"

    # STEP 22 & 23: Open Analytics & Verify Updated Metrics
    print("\n[Step 22 & 23] Checking Analytics Updates...")
    analytics_res = requests.get(f"{BASE_API}/analytics/dashboard", headers=headers)
    assert analytics_res.status_code == 200
    final_analytics = analytics_res.json()
    final_verified = final_analytics["metrics"]["verified_records"]
    print(f"  ✓ Metrics verified: Verified count updated ({initial_verified} -> {final_verified})")
    assert final_verified >= initial_verified + 1, f"Verified count should have incremented, got {final_verified}"

    print("\n" + "=" * 70)
    print("ALL 23 USER JOURNEY VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_test()
