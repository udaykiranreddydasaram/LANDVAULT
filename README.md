# LANDVAULT AI

> **"From Legacy Records to Trusted Digital Land Data"**  
> **Smart India Hackathon 2026** | Problem Statement ID: **SIH26018**  
> **Domain**: Intelligent Land Record Digitization, Cadastral Validation, and Spatial Mapping System

---

## Executive Summary

**LANDVAULT AI** is an enterprise-grade, intelligent land record digitization and validation platform engineered to resolve the multi-decade challenge of fragile, degraded, and fragmented physical land registries across Indian states. By combining computer vision-grounded OCR tokenization, regex-driven cadastral entity parsing, a deterministic tri-factor confidence engine, multi-tiered administrative hierarchy rules, cryptographic content hashing, and an interactive split-screen human-in-the-loop verification studio, LANDVAULT AI converts smudged historical deeds (such as Telangana Patta passbooks, Maharashtra 7/12 extracts, and Uttar Pradesh Khasra-Khatauni records) into clean, legally compliant, GIS-mapped digital title assets backed by an immutable compliance audit trail.

---

## 1. Problem Statement (SIH26018)

Across Indian revenue departments, sub-registrar offices, and district collectorates, historical land administration relies heavily on paper records that span several decades. Digitizing and authenticating these archives presents severe systemic challenges:

* **Fragile & Degraded Physical Deeds**: Decades of environmental exposure, paper yellowing, ink bleeding, torn edges, and physical smudges obscure critical cadastral identifiers such as survey numbers, khata numbers, and boundaries.
* **Inconsistent State Formats & Terminology**: Land records differ significantly by state jurisprudence—from *Record of Rights (ROR) / Pattadar Passbooks* in Telangana and Andhra Pradesh, to *Form VII-XII (7/12 extracts)* in Maharashtra and Gujarat, and *Khasra-Khatauni (Bhulekh)* in Uttar Pradesh and Madhya Pradesh.
* **Non-Standard & Archaic Units of Measurement**: Land records use a mix of legacy and regional units including Acres, Guntas, Hectares, Bigha, Biswa, Cents, and Square Yards, leading to conversion errors and area calculation discrepancies.
* **OCR Ambiguity on Historical Typography**: Standard commercial OCR systems degrade when handling low-contrast dot-matrix prints, typewritten revenue sheets, and handwritten annotations, often misinterpreting survey sub-divisions (e.g., parsing `124/2` as `124/?` or `124-7`).
* **Lack of Automated Hierarchy & Cadastral Validation**: Raw digitized text is rarely validated against canonical state administrative hierarchies (State $\to$ District $\to$ Mandal/Tehsil $\to$ Village) or cadastral formatting rules.
* **Cadastral Collisions & Fraudulent Duplication**: Without real-time spatial collision detection and cryptographic duplicate checks, fraudulent claimants can re-register or double-pledge existing parcels, triggering prolonged civil litigation.
* **Manual Verification Bottlenecks**: Complete reliance on manual verification results in multi-month application backlogs, human error, and lack of visual traceability between digitized fields and original source deeds.

---

## 2. Our Solution

LANDVAULT AI bridges physical land records and modern digital registries through a structured, 10-stage automated digitization, validation, and human-in-the-loop verification pipeline:

```
+---------------------------------------------------------------------------------------------------+
|                                     LANDVAULT AI PIPELINE                                         |
+---------------------------------------------------------------------------------------------------+
|  [1] Document Ingestion (PDF / TIFF / PNG / JPG) + SHA-256 Cryptographic Hash                     |
|                                         v                                                         |
|  [2] Computer Vision Preprocessing (Adaptive Binarization, Deskewing, Noise Reduction)            |
|                                         v                                                         |
|  [3] Modular OCR Engine (Token-Level Bounding Box Extraction & Coordinate Binding)                |
|                                         v                                                         |
|  [4] Cadastral Text Normalization & Regex Entity Extraction (17 Core Attributes)                  |
|                                         v                                                         |
|  [5] Tri-Factor Confidence Scoring (Token Fidelity 40% + Pattern Match 35% + Anchor Match 25%)   |
|                                         v                                                         |
|  [6] Multi-Tiered Business Rule Validation (6 Automated Legal & Structural Rules)                 |
|                                         v                                                         |
|  [7] Multi-Level Duplicate Detection (SHA-256 Content Hash + Cadastral Village Collision Engine)  |
|                                         v                                                         |
|  [8] Interactive Split-Screen Human Verification Studio (SVG Focus Boxes + Live Re-Validation)    |
|                                         v                                                         |
|  [9] Official Title Promotion & Digital Certificate Issuance (ULPIN + Digital Hash)              |
|                                         v                                                         |
| [10] GIS Cadastral Synthesis & Leaflet Mapping (Deterministic Village Meshing & Dispute Layer)    |
+---------------------------------------------------------------------------------------------------+
```

### End-to-End Workflow Breakdown

1. **Document Ingestion**: Scanned deeds (PDF, TIFF, PNG, JPG) are ingested, assigned a unique document ID, and hashed using SHA-256 to prevent duplicate processing.
2. **Image Preprocessing**: Pillow and CV pipelines deskew rotated scans, enhance contrast, and normalize resolution for optimal OCR text extraction.
3. **Modular OCR Extraction**: The OCR provider extracts raw text alongside word-level spatial bounding boxes (`x`, `y`, `w`, `h`, `page`), retaining physical document coordinate origins.
4. **Text Normalization & Field Extraction**: A specialized cadastral parser extracts 17 standard land record fields, mapping regional terminology into uniform schema attributes.
5. **Tri-Factor Confidence Scoring**: Every field is assigned a multi-factor confidence percentage based on OCR token accuracy, regex pattern conformity, and anchor label proximity.
6. **Business Rule Validation**: The validation engine evaluates extracted data against 6 deterministic rules (mandatory completeness, positive land area, cadastral survey syntax, area unit validity, Indian administrative hierarchy, and mutation consistency).
7. **Duplicate & Collision Detection**: Detects file-level hash duplicates and checks existing registered land records in the target village for conflicting survey number claims.
8. **Human Verification Workflow**: Low-confidence fields ($< 70\%$) or validation failures are automatically routed to a prioritized verification queue. In the Split-Screen Studio, verifiers can inspect bounding boxes overlaid on the scanned deed, make inline corrections, and trigger real-time re-validation.
9. **Title Approval & Promotion**: Upon verifier sign-off, the record is promoted to the canonical Land Records Registry, generating a Unique Land Parcel Identification Number (**ULPIN**), a verifiable certificate hash, and an immutable audit log.
10. **Cadastral GIS Mapping**: Verified records are synthesized into deterministic, area-proportional vector polygons on an interactive Leaflet/OSM map, color-coded by legal status (Verified, Pending, Disputed).

---

## 3. System Architecture

LANDVAULT AI is designed as a modular, decoupled client-server architecture with strict separation between user presentation, business logic, validation services, and data persistence.

```
+----------------------------------------------------------------------------------------------------+
|                                    LANDVAULT AI ARCHITECTURE                                       |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ CLIENT LAYER (React 18/19 + Vite + TypeScript + Tailwind CSS) ]                                  |
|  +-----------------------+  +-----------------------+  +-----------------------+                   |
|  | Dashboard & Telemetry |  | Documents Vault & UI  |  | Verification Studio   |                   |
|  +-----------------------+  +-----------------------+  +-----------------------+                   |
|  +-----------------------+  +-----------------------+  +-----------------------+                   |
|  | Cadastral GIS Map     |  | Land Records Registry |  | Tamper Audit Trail    |                   |
|  +-----------------------+  +-----------------------+  +-----------------------+                   |
|                                         | (REST APIs via Axios / Fetch)                            |
|                                         v                                                          |
|  [ API GATEWAY & SECURITY LAYER (FastAPI + Pydantic v2 + OAuth2 / JWT + RBAC) ]                    |
|  +-----------------------------------------------------------------------------------------------+ |
|  | Routers: /auth  |  /documents  |  /verification  |  /land-records  |  /gis  |  /analytics     | |
|  +-----------------------------------------------------------------------------------------------+ |
|                                         |                                                          |
|                                         v                                                          |
|  [ CORE SERVICES & ENGINES LAYER ]                                                                 |
|  +-----------------------+  +-----------------------+  +-----------------------+                   |
|  | OCR Extraction Engine |  | Tri-Factor Confidence |  | Multi-Rule Validation |                   |
|  | (MockSmartOCR/Tess)   |  | Scoring Evaluator     |  | Engine                |                   |
|  +-----------------------+  +-----------------------+  +-----------------------+                   |
|  +-----------------------+  +-----------------------+  +-----------------------+                   |
|  | SHA-256 & Cadastral   |  | Cadastral GIS Parcel  |  | Immutable Compliance  |                   |
|  | Duplicate Detector    |  | Geometry Synthesizer  |  | Audit Logger          |                   |
|  +-----------------------+  +-----------------------+  +-----------------------+                   |
|                                         |                                                          |
|                                         v                                                          |
|  [ DATA & EXTERNAL INTEGRATION LAYER ]                                                             |
|  +-----------------------+  +-----------------------+  +-----------------------+                   |
|  | Relational DB Engine  |  | File & Blob Storage   |  | Government Adapters   |                   |
|  | (SQLite / PostgreSQL) |  | (Uploads / Samples)   |  | (DILRMP / State LRMS) |                   |
|  +-----------------------+  +-----------------------+  +-----------------------+                   |
+----------------------------------------------------------------------------------------------------+
```

---

## 4. Key Features & Modules

### 4.1. Real-Time Analytics & KPI Dashboard
* **Operational Telemetry**: Instant overview of Total Ingested Documents, Verified Titles, Pending Verification Tasks, and Disputed Cadastral Collisions.
* **Confidence Distribution**: Dynamic visual breakdown of extracted fields across High ($\ge 90\%$), Medium ($70-89\%$), and Low ($< 70\%$) confidence tiers.
* **State-Wise Breakdown**: Visual telemetry tracking records across Telangana, Maharashtra, Uttar Pradesh, and Karnataka.
* **Direct Workflow Shortcuts**: One-click jumps to the verification studio, document repository, and GIS map.

### 4.2. Document Vault & Preset Ingestion
* **Multi-Format Ingestion**: Supports JPG, PNG, TIFF, and PDF scans of historical land documents.
* **SIH Judging Presets**: One-click quick-presets for rapid live demonstration:
  * *Clean Telangana Patta Deed (2005)*: Clean extract demonstrating automated high-confidence extraction.
  * *Smudged Telangana Patta Deed (1988)*: Simulated low-confidence survey number (`124/?`) triggering the human verification workflow.
  * *Maharashtra 7/12 Extract (Pune)*: Demonstrating Marathi-English dual revenue schema parsing (`88/1A`).
  * *Uttar Pradesh Khasra-Khatauni (Lucknow)*: Demonstrating Northern Indian revenue hierarchy validation (`215/3`).
* **Cryptographic Deduplication**: SHA-256 hashing flags duplicate file uploads before processing.

### 4.3. Cadastral Entity Extraction (17 Core Attributes)
The extraction engine normalizes and parses 17 canonical cadastral attributes from raw OCR text:
1. `state` (e.g., Telangana, Maharashtra, Uttar Pradesh)
2. `district` (e.g., Ranga Reddy, Pune, Lucknow)
3. `mandal_tehsil` (e.g., Shamshabad, Haveli, Mohanlalganj)
4. `village` (e.g., Mamidipally, Wagholi, Bakas)
5. `landowner_name` (e.g., Sri K. Venkat Reddy, Rajeshwar Dattatray Patil)
6. `survey_number` (e.g., `124/2`, `88/1A`, `215/3`)
7. `khasra_number` (e.g., `124/KH-4`, `215`)
8. `khata_number` (e.g., `408`, `184`, `312`)
9. `plot_number` (e.g., `P-12`, `PL-08`)
10. `land_area` (e.g., `2.45`, `1.75`, `4.50`)
11. `area_unit` (e.g., `Acres`, `Hectares`, `Bigha`, `Guntas`)
12. `land_classification` (e.g., `Agricultural - Dry`, `Jirayat`)
13. `ownership_type` (e.g., `Pattadar`, `Sole Proprietor`, `Bhumidhar`)
14. `mutation_number` (e.g., `MUT-2018-09823`, `MUT-MH-2019-112`)
15. `registration_number` (e.g., `4521/1988`, `2014-9981`)
16. `registration_date` (e.g., `1988-10-14`, `2014-06-20`)
17. `remarks` (e.g., Ancestral partition deed notes, Sub-Registrar stamp data)

### 4.4. Tri-Factor Confidence Scoring Formula
Unlike naive OCR systems that report only character-level confidence, LANDVAULT AI computes a weighted tri-factor confidence score for each extracted field:

$$\text{Confidence} = (0.40 \times \text{Token Confidence}) + (0.35 \times \text{Pattern Score}) + (0.25 \times \text{Anchor Score})$$

* **Token Confidence ($40\%$)**: Raw OCR optical recognition probability emitted by the image token extractor.
* **Pattern Score ($35\%$)**: Evaluates format conformity (e.g., regex check for survey numbers like `^\d{1,4}(/\d{1,4})?([A-Za-z]+)?$`, numeric non-zero checks for area, and ISO date conformity `YYYY-MM-DD`).
* **Anchor Score ($25\%$)**: Verifies whether standard legal anchor keywords (e.g., *"Survey No:"*, *"Pattadar:"*, *"Extent:"*) were detected adjacent to the value.

#### Confidence Tiers & Routing
* 🟢 **HIGH ($\ge 90\%$)**: Ready for direct or expedited promotion.
* 🟡 **MEDIUM ($70-89\%$)**: Extracted with minor caveats; displayed with warning indicators.
* 🔴 **LOW ($< 70\%$)**: Automatically flagged with a high-priority task in the **Human Verification Queue**.

### 4.5. Multi-Tiered Business Rule Validation Engine
Every document is evaluated against 6 deterministic legal and structural validation rules:

| Rule Code | Rule Name | Severity | Validation Logic |
|---|---|---|---|
| `VAL_MANDATORY_FIELD` | Mandatory Field Completeness | **CRITICAL** | Ensures all 8 mandatory fields (`state`, `district`, `mandal_tehsil`, `village`, `landowner_name`, `survey_number`, `land_area`, `area_unit`) are present and non-empty. |
| `VAL_AREA_POS` | Positive Land Area | **ERROR** | Verifies that numeric land area is parsed and strictly $> 0$. |
| `VAL_SURVEY_FMT` | Survey Number Format | **ERROR** | Enforces cadastral regex syntax `^\d{1,4}(\s*[/\\-]\s*(\d{1,4}\|[A-Za-z]+))?(\s*[/\\-]\s*[A-Za-z0-9]+)?$`. Catches smudges (`?`) and illegal characters. |
| `VAL_AREA_UNIT` | Area Unit Legality | **WARNING** | Validates unit against the Indian standard whitelist (*Acres, Hectares, Guntas, Bigha, Biswa, Sq. Yards, Sq. Meters, Cent*). |
| `VAL_GEO_HIERARCHY` | Administrative Hierarchy | **CRITICAL** | Cross-references `State` $\to$ `District` $\to$ `Mandal/Tehsil` $\to$ `Village` against the canonical master dataset. |
| `VAL_OWNER_MUTATION` | Mutation & Registration | **WARNING** | Checks logical coherence between historical mutation orders and registration references. |

### 4.6. Interactive Split-Screen Human Verification Studio
* **Side-by-Side Visual Grounding**: Scanned deed viewer on the left; structured editable fields and live validation diagnostics on the right.
* **Interactive SVG Bounding Box Overlays**: Hovering over or clicking any field dynamically renders an animated SVG highlight box around the physical token on the scanned deed canvas.
* **Inline Real-Time Correction**: Verifiers can update smudged fields (e.g., correcting `124/?` to `124/2`). The backend immediately re-runs the validation engine and clears rule failures in real time.
* **Decision Controls**: Verifiers can **Approve & Promote to Cadastre** or **Reject with Reason Notes**, maintaining complete workflow accountability.

### 4.7. Cadastral GIS Mapping & Spatial Mesh Engine
* **Leaflet & OpenStreetMap Integration**: Interactive cadastral map centered on authentic Indian village coordinates.
* **Deterministic Geometry Synthesis**: Uses survey numbers, village centroids, and land extent to construct realistic 4-5 vertex cadastral boundary polygons with deterministic spatial offsets.
* **Area Unit Conversion**: Converts regional units (Acres, Hectares, Bigha, Guntas) to standardized square meters (`m²`).
* **Visual Status Classification**:
  * 🟢 **Emerald Green**: Verified, legally approved cadastral parcels.
  * 🟡 **Amber Yellow**: In-progress / unverified parcels undergoing review.
  * 🔴 **Crimson Red**: Disputed parcels flagged for spatial or claimant overlap collisions.
* **Interactive Parcel Inspector & Search**: Search by survey number to jump to boundaries, view landowner metadata, and download title certificates.

### 4.8. Land Records Registry & Official Title Certificate
* **Canonical Registry**: Searchable database of all approved land titles with multi-field filtering (State, District, Village, Survey No, Owner).
* **Digital Title Certificate**: Generates an official verifiable certificate featuring:
  * Unique Land Parcel Identification Number (**ULPIN**) conforming to DILRMP 2.0 specs.
  * SHA-256 digital certificate verification hash.
  * Full administrative hierarchy and land classification data.
  * Digital signature status of the verifying revenue authority.

### 4.9. Tamper-Evident Compliance Audit Trail
* **Immutable Event Log**: Every ingestion, field correction, manual override, approval, and rejection is recorded in an append-only audit ledger.
* **Audit Metadata**: Tracks Entity Name, Entity ID, Action Type, Performed By (Officer ID), Client IP Address, UTC Timestamp, and complete JSON Before/After Diffs.

### 4.10. Government System Interoperability Adapters (Mock)
* **DILRMP 2.0 Mock Adapter**: Simulates integration with the *Digital India Land Records Modernization Programme* central registry, generating compliant 14-digit ULPINs and verifying cadastral sheet alignment.
* **State LRMS Mock Adapter**: Simulates automated mutation sync webhooks for state portals (*Dharani Telangana, Mahabhulekh Maharashtra, UP Bhulekh*), returning signed transaction receipts.

---

## 5. Technology Stack

### Frontend
| Component | Technology | Description |
|---|---|---|
| **Framework** | React 18 / 19 | Component-based modern user interface |
| **Tooling & Bundler** | Vite 6 | High-speed ESM development server and build tool |
| **Language** | TypeScript (~5.8) | Type-safe application development |
| **Styling** | Tailwind CSS (v3) | Responsive, utility-first design system |
| **Icons** | Lucide React | Clean, modern iconography |
| **GIS & Mapping** | Leaflet 1.9 + `@types/leaflet` | OpenStreetMap cadastral vector rendering |
| **Charts & Telemetry**| Recharts | Dynamic analytics graphs and confidence charts |

### Backend
| Component | Technology | Description |
|---|---|---|
| **Web Framework** | FastAPI (>=0.110.0) | High-performance asynchronous REST API framework |
| **ASGI Server** | Uvicorn (>=0.28.0) | Lightning-fast ASGI production server |
| **Language** | Python 3.14 / 3.11+ | Clean, modular Python runtime |
| **Data Validation** | Pydantic v2 (>=2.6.0) | Strict schema validation and serialization |
| **ORM & Database** | SQLAlchemy 2.0 | Dual-compatible ORM (SQLite / PostgreSQL) |
| **Authentication** | Python-Jose & Passlib (Bcrypt)| JWT token signing and salted password hashing |
| **Image Processing** | Pillow (PIL >=10.2.0) | Synthetic deed generation, deskewing, and image manipulation |
| **Testing** | Pytest & Requests | Unit, integration, and 23-step automated E2E journey tests |

---

## 6. Database Schema & Data Models

LANDVAULT AI utilizes 8 interconnected SQLAlchemy models with full relationship mapping:

```
+-------------------+       +-----------------------+       +----------------------+
|       User        |       |       Document        | 1---* |    LandRecordField   |
+-------------------+       +-----------------------+       +----------------------+
| id (PK)           | 1   * | id (PK)               |       | id (PK)              |
| username          |-------| uploaded_by_id (FK)   |       | document_id (FK)     |
| email             |       | file_name             |       | field_name           |
| hashed_password   |       | file_path             |       | extracted_value      |
| role              |       | file_hash (SHA-256)   |       | normalized_value     |
| department        |       | status                |       | confidence (float)   |
+-------------------+       | ocr_provider          |       | bounding_box (JSON)  |
        |                   +-----------------------+       | is_verified (bool)   |
        |                               | 1                 +----------------------+
        |                               | 1
        |                   +-----------------------+       +----------------------+
        |                   |      LandRecord       | 1---* |   ValidationResult   |
        |                   +-----------------------+       +----------------------+
        |                   | id (PK)               |       | id (PK)              |
        |                   | document_id (FK)      |       | document_id (FK)     |
        +-------------------| verified_by_id (FK)   |       | rule_code            |
                            | record_identifier     |       | rule_name            |
                            | state, district...    |       | severity             |
                            | survey_number         |       | status (PASS/FAIL)   |
                            | land_area, area_unit  |       | message              |
                            | is_verified (bool)    |       +----------------------+
                            | is_disputed (bool)    |
                            +-----------------------+
                                        | 1
                                        | 1
                            +-----------------------+
                            |       GISParcel       |
                            +-----------------------+
                            | id (PK)               |
                            | land_record_id (FK)   |
                            | survey_number         |
                            | village, district...  |
                            | center_latitude       |
                            | center_longitude      |
                            | geojson_geometry      |
                            | area_sq_meters        |
                            | status                |
                            +-----------------------+
```

### Additional Supporting Models
* **`VerificationTask`**: Manages the human review queue (`document_id`, `priority`, `status`, `assigned_to_id`, `notes`).
* **`AuditLog`**: Append-only compliance log (`entity_name`, `entity_id`, `action`, `performed_by_id`, `old_values`, `new_values`, `ip_address`, `timestamp`).

---

## 7. REST API Reference

All backend routes are mounted under the `/api/v1` namespace. Interactive Swagger UI documentation is available at `http://127.0.0.1:8000/docs`.

### Authentication & RBAC (`/api/v1/auth`)
* `POST /api/v1/auth/login-json`: Authenticate with username and password; returns JWT bearer token and user role.
* `POST /api/v1/auth/token`: OAuth2-compatible form-urlencoded login endpoint.
* `GET /api/v1/auth/me`: Get current authenticated user profile and permissions.

### Document Processing & Ingestion (`/api/v1/documents`)
* `POST /api/v1/documents/upload`: Upload scanned deed (multipart/form-data) to trigger preprocessing, OCR, extraction, confidence calculation, and rule validation.
* `GET /api/v1/documents`: List all ingested documents with status and metadata.
* `GET /api/v1/documents/{doc_id}`: Retrieve detailed document view including extracted fields, bounding boxes, and validation diagnostics.
* `POST /api/v1/documents/{doc_id}/reprocess`: Re-trigger the OCR and extraction pipeline with alternate parameters.

### Human Verification Studio (`/api/v1/verification`)
* `GET /api/v1/verification/tasks`: List verification tasks with priority filtering (`HIGH`, `MEDIUM`, `LOW`, `ALL`).
* `GET /api/v1/verification/tasks/{task_id}`: Retrieve full split-screen studio dataset (document, fields with bounding boxes, validation results).
* `POST /api/v1/verification/tasks/{task_id}/batch-fields`: Update multiple fields inline and trigger immediate validation recalculation.
* `POST /api/v1/verification/tasks/{task_id}/decision`: Record verifier decision (`APPROVE` or `REJECT`) with notes, promoting approved records to the canonical cadastre.

### Land Records Registry (`/api/v1/land-records`)
* `GET /api/v1/land-records`: Search and filter verified and disputed land records.
* `GET /api/v1/land-records/{record_id}`: Retrieve full land record profile.
* `GET /api/v1/land-records/{record_id}/certificate`: Generate an official Digital Title Certificate with ULPIN and verification hash.

### Cadastral GIS & Spatial Mesh (`/api/v1/gis`)
* `GET /api/v1/gis/parcels`: Retrieve GeoJSON FeatureCollection containing all cadastral vector polygons and properties.
* `GET /api/v1/gis/parcels/{parcel_id}`: Retrieve single parcel geometry and boundary coordinates.
* `GET /api/v1/gis/search`: Search parcels by survey number, village, or owner name.

### Analytics & System Metrics (`/api/v1/analytics`)
* `GET /api/v1/analytics/dashboard`: Fetch live KPI metrics, confidence score distributions, state-wise counts, and queue statistics.

### Tamper-Evident Audit Trail (`/api/v1/audit`)
* `GET /api/v1/audit/logs`: Retrieve paginated, filterable immutable audit trail records.

### Government Interoperability Adapters (`/api/v1/adapters`)
* `POST /api/v1/adapters/dilrmp/verify`: Query simulated DILRMP 2.0 central cadastre alignment and generate ULPIN.
* `POST /api/v1/adapters/lrms/mutation`: Trigger simulated State LRMS mutation certificate webhook.

---

## 8. Role-Based Access Control (RBAC) & Demo Accounts

LANDVAULT AI features built-in Role-Based Access Control with a **1-click Role Switcher** in the top navigation bar for testing:

| Role | Username | Password | Access Scope & Responsibilities |
|---|---|---|---|
| **Verifier** *(Default)* | `verifier` | `verifierpassword123` | **Revenue Inspector / Tahsildar**: Access to Human Verification Queue, Split-Screen Studio, inline field correction, and approval/rejection decisions. |
| **Admin** | `admin` | `adminpassword123` | **Director of Land Records**: Full platform control, user management, system reprocessing, preset initialization, and tamper-evident audit ledger inspection. |
| **Viewer** | `viewer` | `viewerpassword123` | **Citizen / Bank Audit Officer**: Read-only public registry access, Digital Title Certificate viewing, and Cadastral GIS Map exploration. |

---

## 9. Installation & Quick Start Guide

### Prerequisites
* **Python 3.10+** (Python 3.11, 3.12, 3.13, 3.14 supported)
* **Node.js 18+** & **npm**
* **Git** (optional)

### Option A: 1-Click Launch (Windows)
Run the automated launcher batch script from the project root:
```cmd
run_app.bat
```
This script configures environment paths, starts the FastAPI backend on port 8000, launches the Vite development server on port 5173, and opens your default browser.

---

### Option B: Manual Step-by-Step Setup

#### 1. Backend Setup
```bash
# Navigate to the backend directory
cd backend

# Create and activate a Python virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

# Install required Python dependencies
pip install -r requirements.txt

# Start the FastAPI backend server (auto-seeds demo records on first start)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
* Backend API is live at: `http://127.0.0.1:8000`
* Interactive API Docs: `http://127.0.0.1:8000/docs`

#### 2. Frontend Setup
```bash
# In a new terminal window, navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev -- --host 127.0.0.1 --port 5173
```
* Web Application is live at: `http://127.0.0.1:5173`

---

## 10. SIH Judging Demonstration Walkthrough

Follow this 5-step demonstration flow to evaluate the end-to-end capabilities of LANDVAULT AI:

### Step 1: Telemetry & Ingestion (Dashboard & Vault)
1. Open `http://127.0.0.1:5173/` (auto-logged in as **Verifier**).
2. Review the live KPI telemetry cards and confidence distributions on the **Dashboard**.
3. Navigate to **Documents** in the sidebar.
4. Under *SIH Judging Quick-Presets*, click **"Smudged Patta Deed (1988)"**.
5. The document is instantly ingested, preprocessed, and extracted. Notice that because the physical deed contains an ink smudge on the survey number (`124/?`), the overall confidence score drops to $54\%$, triggering validation failure `VAL_SURVEY_FMT`.

### Step 2: Human Verification Queue & Split-Screen Studio
1. Navigate to **Verification Queue**; notice the smudged deed is routed to the **HIGH Priority** queue.
2. Click **"Open Studio"** on Task `#1`.
3. Observe the Split-Screen Studio:
   * **Left Canvas**: The original vintage revenue stamp deed is rendered with SVG bounding boxes.
   * **Right Canvas**: Extracted fields and rule validation diagnostics are displayed.
4. **Hover over or click** the *Survey Number* field $\to$ the left canvas dynamically animates an SVG bounding box focusing on the physical ink smudge!

### Step 3: Inline Correction & Real-Time Re-Validation
1. In the right panel, edit the Survey Number field from `124/?` to `124/2`.
2. Click the **Save / Update** button.
3. The validation engine immediately re-evaluates the field: the `VAL_SURVEY_FMT` failure clears, and all 6 validation rules show **PASSED** in real time.
4. Enter verifier notes: *"Verified against physical 1988 stamp paper. Survey 124/2 confirmed."*
5. Click **"Approve & Promote to Cadastre"**.

### Step 4: Cadastral GIS Spatial Mapping
1. Click **GIS Map** in the sidebar.
2. A new **Emerald Green Cadastral Polygon** for Survey Number `124/2` is rendered at village *Mamidipally* coordinates.
3. Click the polygon to inspect landowner details (*Sri K. Venkat Reddy*) and view the area extent ($2.45\text{ Acres} \approx 9,914.8\text{ m}^2$).
4. Observe the **Crimson Red Polygon** showing a simulated cadastral dispute collision flagged by the duplicate engine.

### Step 5: Digital Title Certificate & Audit Trail
1. Navigate to **Land Records** and click on record `LR-TS-RR-2026-00001` or the newly approved record.
2. Click **"View Certificate"** to view the generated **Digital Land Record Certificate** with its official **ULPIN** and digital hash.
3. Use the top navbar role switcher to switch to **Admin**.
4. Open **Audit Trail** to inspect the immutable audit ledger verifying the exact field modification delta, verifier timestamp, and IP address.

---

## 11. Automated Testing & Verification

LANDVAULT AI includes a comprehensive, automated 23-step end-to-end test suite simulating the full user journey:

```bash
# Execute the full 23-step end-to-end user journey test
python test_full_user_journey.py
```

### Test Coverage Highlights
* **Steps 1–3**: Verifier authentication, JWT validation, and live dashboard metric retrieval.
* **Steps 4–6**: Document vault listing, multipart deed upload, and asynchronous pipeline execution.
* **Steps 7–9**: OCR extraction assertion ($\ge 10$ fields), low-confidence detection ($< 70\%$), and validation rule failure checks.
* **Steps 10–12**: Verification task creation, priority queue placement, and split-screen bounding box verification.
* **Steps 13–15**: Inline batch field editing (`124/?` $\to$ `124/2`), automated rule clearance, and verifier approval.
* **Steps 16–18**: Registry search, record promotion verification, and DILRMP ULPIN certificate generation.
* **Steps 19–21**: Immutable audit ledger recording and GIS Leaflet GeoJSON parcel polygon synthesis.
* **Steps 22–23**: Live analytics KPI counter increment validation.

```bash
# Run backend unit tests via Pytest
pytest backend/tests/test_backend.py -v
```

---

## 12. Directory Structure

```
LANDVAULT-AI/
├── README.md                          # Comprehensive Technical Documentation
├── run_app.bat                        # Windows 1-Click Launch Script
├── test_full_user_journey.py          # 23-Step Automated End-to-End Test Suite
├── verify_e2e.py                      # Quick E2E API Verification Script
│
├── backend/                           # FastAPI Python Backend
│   ├── requirements.txt               # Backend Python Dependencies
│   ├── landvault.db                   # SQLite Database File
│   ├── samples/                       # Sample Scanned Deeds & Stamp Papers
│   ├── storage/                       # Ingested Uploads & Processed Files
│   ├── tests/
│   │   └── test_backend.py            # Pytest Suite
│   └── app/
│       ├── main.py                    # FastAPI Entrypoint, Static Mounts & Lifespan
│       ├── adapters/                  # Government Mock Adapters
│       │   ├── dilrmp_mock.py         # DILRMP 2.0 Central Cadastre & ULPIN Adapter
│       │   └── lrms_mock.py           # State LRMS Mutation Sync Adapter
│       ├── api/                       # API Routing Layer
│       │   ├── deps.py                # Database Sessions & JWT RBAC Dependencies
│       │   └── v1/
│       │       ├── api.py             # Router Aggregator
│       │       └── endpoints/         # Modular Endpoint Controllers
│       │           ├── adapters.py    # DILRMP & LRMS Endpoints
│       │           ├── analytics.py   # KPI Telemetry Endpoints
│       │           ├── audit.py       # Audit Log Retrieval Endpoints
│       │           ├── auth.py        # Authentication & Role Switcher
│       │           ├── documents.py   # Ingestion, OCR & Reprocessing
│       │           ├── gis.py         # GeoJSON Cadastral Mesh Endpoints
│       │           ├── land_records.py# Canonical Registry & Certificate Endpoints
│       │           └── verification.py# Human-in-the-Loop Studio Endpoints
│       ├── core/                      # Application Configuration & Security
│       │   ├── config.py              # Environment Settings & Thresholds
│       │   ├── database.py            # SQLAlchemy Engine & Session Factory
│       │   └── security.py            # Password Hashing & JWT Handlers
│       ├── demo/                      # Demonstration Seeds
│       │   └── seed_data.py           # Synthetic Stamp Papers & Initial DB Records
│       ├── models/                    # SQLAlchemy ORM Data Models (8 Entities)
│       │   ├── audit_log.py           # AuditLog Model
│       │   ├── document.py            # Document Model
│       │   ├── gis_parcel.py          # GISParcel Model
│       │   ├── land_record.py         # LandRecord Model
│       │   ├── land_record_field.py   # LandRecordField Model
│       │   ├── user.py                # User Model
│       │   ├── validation_result.py   # ValidationResult Model
│       │   └── verification_task.py   # VerificationTask Model
│       ├── schemas/                   # Pydantic Schemas for DTOs & Payloads
│       └── services/                  # Business Logic Engines
│           ├── audit/logger.py        # Append-Only Audit Logger
│           ├── duplicate/detector.py  # SHA-256 & Cadastral Collision Detector
│           ├── extraction/
│           │   ├── confidence.py      # Tri-Factor Confidence Scoring Formula
│           │   └── extractor.py       # Cadastral Regex Parser & Bounding Box Binder
│           ├── gis/parcel_builder.py  # Deterministic Polygon Synthesizer & Area Converter
│           ├── ocr/
│           │   ├── base.py            # Base OCR Provider Interface & Dataclasses
│           │   └── mock_provider.py   # Realistic High-Res Historical OCR Simulator
│           └── validation/
│               ├── engine.py          # Validation Pipeline Orchestrator
│               ├── master_data.py     # Indian Administrative Hierarchy Master Dataset
│               └── rules.py           # 6 Deterministic Business Validation Rules
│
└── frontend/                          # React + TypeScript + Vite Frontend
    ├── package.json                   # Frontend Dependencies & Scripts
    ├── vite.config.ts                 # Vite Build Configuration
    ├── tailwind.config.js             # Tailwind CSS Custom Design Tokens
    ├── tsconfig.json                  # TypeScript Compiler Configuration
    └── src/
        ├── App.tsx                    # Route Definitions & Main Shell
        ├── main.tsx                   # React DOM Entrypoint
        ├── index.css                  # Global Tailwind & Custom Styles
        ├── components/
        │   └── common/
        │       ├── Navbar.tsx         # Navigation Header & 1-Click Role Switcher
        │       └── Sidebar.tsx        # Navigation Menu
        ├── context/
        │   └── AuthContext.tsx        # Authentication & Role State Provider
        ├── pages/
        │   ├── AnalyticsPage.tsx      # In-Depth Telemetry & Visual Charts
        │   ├── AuditPage.tsx          # Tamper-Evident Audit Ledger Viewer
        │   ├── DashboardPage.tsx      # System Overview & KPI Cards
        │   ├── DocumentDetailPage.tsx # Single Document Inspector & Field Viewer
        │   ├── DocumentsPage.tsx      # Vault, Upload & SIH Quick-Presets
        │   ├── GISMapPage.tsx         # Leaflet OpenStreetMap Cadastral Visualizer
        │   ├── LandRecordsPage.tsx    # Canonical Registry & Certificate Viewer
        │   ├── LoginPage.tsx          # Login & Credential Selector
        │   ├── VerificationQueuePage.tsx # Priority-Categorized Task Queue
        │   └── VerificationStudioPage.tsx# Split-Screen Studio with SVG Focus Boxes
        ├── services/
        │   └── api.ts                 # Typed API Client for Backend Endpoints
        └── types/                     # TypeScript Interfaces & Enums
```

---

## 13. Future Roadmap

* **Expanded Multi-Language Vernacular OCR Support**: Integration with specialized vernacular fine-tuned vision models (e.g., Tesseract OCR with Telugu, Marathi, Hindi, and Kannada language packs).
* **On-Chain Hash Attestation**: Anchoring SHA-256 title hashes and mutation events to a permissioned blockchain (e.g., Hyperledger Fabric) for decentralized tamper resistance.
* **Drone / Satellite Cadastral Mesh Overlay**: Integration with Survey of India / SVAMITVA drone ortho-rectified imagery (ORI) for sub-centimeter parcel boundary alignment.
* **Automated Encumbrance Graph Analysis**: Graph-based analysis linking mortgage charges, court injunctions, and historical succession trees directly to cadastral parcels.

---

## 14. License & Acknowledgments

* **Project**: LANDVAULT AI
* **Hackathon**: Smart India Hackathon 2026 (SIH26018)
* **License**: MIT Open Source License
* Developed for modernization of public land records administration, transparent cadastral governance, and citizen empowerment across India.
