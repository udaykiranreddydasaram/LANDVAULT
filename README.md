# LANDVAULT AI
> **"From Legacy Records to Trusted Digital Land Data"**  
> **Smart India Hackathon 2026** — Problem Statement: **SIH26018**  
> *Intelligent Land Record Digitization and Validation System*

---

## 🏛️ System Overview

**LANDVAULT AI** is an intelligent, end-to-end land records digitization, validation, and cadastral mapping system designed to solve the challenges of historical, paper-based revenue land records across India.

### 🌟 Core Capabilities
1. **Scanned Deed Ingestion**: Supports PDFs, TIFFs, JPG, and PNG historical stamp deeds with cryptographic SHA-256 duplicate content detection.
2. **Modular OCR & CV Preprocessing**: Computer vision enhancement (deskewing, Otsu thresholding, noise removal) with pluggable OCR engines (Smart Simulator, PyTesseract, and Cloud Vision).
3. **AI Field Extraction & Tri-Factor Confidence Scoring**: Extracts all 17 core cadastral attributes with confidence computed from OCR token fidelity, regex pattern conformity, and anchor proximity:
   - 🟢 **HIGH (90–100%)**: Eligible for automated promotion.
   - 🟡 **MEDIUM (70–89%)**: Validated with cautionary visual indicators.
   - 🔴 **LOW (0–69%)**: Automatically routed to the Human Verification Queue.
4. **Comprehensive Validation Engine**:
   - Mandatory fields non-empty check
   - Positive land area constraint (`land_area > 0`)
   - Legal cadastral survey number syntax (`124/2`, `88/1A`, etc.)
   - Indian Administrative Master Hierarchy verification (`State` $\to$ `District` $\to$ `Mandal` $\to$ `Village`)
   - Cadastral duplicate collision detection (detects overlapping claims in the same village).
5. **Interactive Split-Screen Human Verification Studio**:
   - Side-by-side view with original scanned deed and live SVG bounding boxes.
   - Hovering or editing any field dynamically highlights its physical origin on the scanned deed.
   - Real-time inline field correction with instant re-validation.
6. **Cadastral GIS Engine**:
   - Interactive Leaflet & OpenStreetMap cadastral mesh.
   - Deterministic, area-proportional parcel polygons color-coded by legal status (Verified, Pending, Disputed).
   - Search by survey number to jump directly to the parcel boundary.
7. **Tamper-Evident Audit Trail**: Immutable compliance ledger recording operator identity, UTC timestamp, IP, and JSON deltas for every modification.
8. **Government Interoperability Adapters**: Pluggable mock adapters for **DILRMP** (ULPIN generation) and **State LRMS** (mutation certificate webhooks).

---

## 🚀 Live Access URLs

Both servers are currently active:

| Service | URL | Description |
|---|---|---|
| **Web Application** | [http://127.0.0.1:5173/](http://127.0.0.1:5173/) | Interactive React Single Page Application |
| **API Backend** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | FastAPI Server |
| **Swagger Docs** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive API Explorer |

---

## 👤 Default Demo Accounts & Roles

Switch between roles with **1 click** in the top navigation bar:

| Role | Username | Password | Purpose |
|---|---|---|---|
| **Verifier** *(Default)* | `verifier` | `verifierpassword123` | Revenue Inspector: Verification studio, field edits, approval/rejection |
| **Admin** | `admin` | `adminpassword123` | Director of Land Records: Full access, user management, tamper audit trail |
| **Viewer** | `viewer` | `viewerpassword123` | Citizen / Bank Officer: Read-only access to verified titles and GIS map |

---

## 🎬 5-Step SIH Demonstration Flow

1. **Dashboard**: Observe live KPI metrics (Ingested Records, Verified Titles, Human Queue, Disputed Collisions).
2. **Documents Vault**: Click **"Smudged Patta Deed (1988)"** under *SIH Judging Quick-Presets* to simulate a legacy deed with an ink smudge on the survey number (`124/?`).
3. **Verification Studio**:
   - Notice the document is routed to the High-Priority queue due to low OCR confidence (`54%`).
   - Hover over the *Survey Number* field $\to$ the left canvas draws an animated focus box around the smudge on the physical deed!
   - Correct `124/?` to `124/2` and click the save icon $\to$ the validation exception clears in real time!
   - Click **"Approve & Promoted to Cadastre"**.
4. **Cadastral GIS Map**:
   - Open the map $\to$ a new **Emerald Green Cadastral Polygon** appears at the village coordinates for Survey No `124/2`!
   - Click the polygon to inspect owner metadata and view the official Digital Title Certificate.
   - Point out the **Crimson Red Polygon** showing a simulated duplicate collision flagged by the collision engine.
5. **Tamper Audit Trail**: Switch to the **Admin** role and inspect the audit ledger showing the exact field delta and timestamp.

---

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Lucide React, Recharts, Leaflet, OpenStreetMap
- **Backend**: Python 3.14, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Dual SQLite / PostgreSQL support)
- **Validation**: Indian Administrative Hierarchy, Regex Cadastral Synthesizer, SHA-256 Duplicate Detector
