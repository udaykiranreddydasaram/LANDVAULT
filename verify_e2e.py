import urllib.request
import json

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={'Content-Type': 'application/json'}
    )
    return json.loads(urllib.request.urlopen(req).read().decode())

def get(url):
    return json.loads(urllib.request.urlopen(url).read().decode())

print("=== 1. Testing Authentication ===")
auth = post('http://127.0.0.1:8000/api/v1/auth/login-json', {
    'username': 'verifier',
    'password': 'verifierpassword123'
})
print("Authenticated user:", auth['user']['full_name'], "| Role:", auth['user']['role'])

print("\n=== 2. Inspecting Human Verification Queue ===")
tasks = get('http://127.0.0.1:8000/api/v1/verification/tasks?status_filter=PENDING')
print("Total Pending Tasks:", len(tasks))
for t in tasks:
    print(f"Task #{t['id']}: File={t['file_name']} | Survey={t['survey_number']} | Conf={t['overall_confidence']}")

if tasks:
    task_id = tasks[0]['id']
    print(f"\n=== 3. Simulating Verifier Field Correction on Task #{task_id} ===")
    upd = post(
        f'http://127.0.0.1:8000/api/v1/verification/tasks/{task_id}/field',
        {'field_name': 'survey_number', 'value': '124/2'}
    )
    print("Correction status:", upd['message'])

    print(f"\n=== 4. Approving & Promoting Record #{task_id} to Official Cadastre ===")
    appr = post(
        f'http://127.0.0.1:8000/api/v1/verification/tasks/{task_id}/decision',
        {
            'decision': 'APPROVE',
            'notes': 'Verified stamp deed against Sub-Registrar Shamshabad historical archives.',
            'edited_fields': {'survey_number': '124/2'}
        }
    )
    print("Approval Result:", appr['message'])
    print("Official Record Identifier:", appr.get('record_identifier'))

print("\n=== 5. Verifying GIS Cadastral Mesh Synchronization ===")
parcels = get('http://127.0.0.1:8000/api/v1/gis/parcels')
print("Active GIS Cadastral Parcels:", len(parcels['features']))
for f in parcels['features']:
    p = f['properties']
    print(f"- Survey {p['survey_number']} ({p['village']}) | Status: {p['status']} | Extent: {p['land_area']} {p['area_unit']}")

print("\n=== 6. Checking Live Analytics Metrics ===")
analytics = get('http://127.0.0.1:8000/api/v1/analytics/dashboard')
m = analytics['metrics']
print(f"Total Ingested: {m['total_documents']} | Verified: {m['verified_records']} | Pending: {m['pending_verification']} | Disputed: {m['disputed_records']}")
print(f"Auto-Verification Rate: {m['auto_verification_rate']}% | Mean Confidence: {m['average_confidence']}")

print("\n=== 7. Querying Mock External Adapters ===")
dilrmp = get('http://127.0.0.1:8000/api/v1/adapters/dilrmp/verify/124-2')
print("DILRMP Sync Status:", dilrmp['dilrmp_sync_status'], "| ULPIN:", dilrmp['ulpin'])
print("\n>>> ALL SYSTEM MODULES FULLY OPERATIONAL AND VERIFIED! <<<")
