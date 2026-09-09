import re
from typing import Dict, Any, List, Optional
from backend.app.services.ocr.base import OCRResult, OCRToken
from backend.app.services.extraction.confidence import calculate_field_confidence

FIELD_PATTERNS = {
    "state": [r"State\s*[:\-]\s*([A-Za-z\s]+)", r"Government of\s+([A-Za-z]+)"],
    "district": [r"District\s*[:\-]\s*([A-Za-z\s\-]+)"],
    "mandal_tehsil": [r"(?:Mandal|Tehsil|Taluka)\s*[:\-]\s*([A-Za-z\s\-]+)"],
    "village": [r"Village\s*[:\-]\s*([A-Za-z\s\-]+)"],
    "landowner_name": [
        r"(?:Pattadar|Landowner|Bhogvatdar|Bhumidhar|Owner)(?:\s+Name)?\s*[:\-]\s*([A-Za-z\s\.\,\'\-]+)",
        r"Name\s*[:\-]\s*([A-Za-z\s\.\,\'\-]+)"
    ],
    "survey_number": [r"(?:Survey\s*No|Survey\s*Number|Gat\s*No|Gata\s*No)\s*[:\-]\s*([0-9A-Za-z\/\?\-\s]+)"],
    "khasra_number": [r"Khasra\s*(?:No|Number)?\s*[:\-]\s*([0-9A-Za-z\/\-]+)"],
    "khata_number": [r"Khata\s*(?:No|Number)?\s*[:\-]\s*([0-9A-Za-z\/\-]+)"],
    "plot_number": [r"Plot\s*(?:No|Number)?\s*[:\-]\s*([0-9A-Za-z\/\-]+)"],
    "land_area": [r"(?:Extent|Land\s*Area|Total\s*Area|Area\s*Extent|Area)\s*[:\-]\s*([0-9\.\,]+)"],
    "area_unit": [r"(?:Acres|Hectares|Guntas|Bigha|Biswa|Sq\.\s*Yards|Sq\.\s*Meters|Cent)"],
    "land_classification": [r"(?:Classification|Land\s*Nature|Land\s*Usage)\s*[:\-]\s*([A-Za-z0-9\s\-\(\)]+)"],
    "ownership_type": [r"(?:Ownership\s*Type|Ownership)\s*[:\-]\s*([A-Za-z0-9\s\-]+)"],
    "mutation_number": [r"(?:Mutation\s*Order\s*No|Mutation\s*No|Mutation\s*Number|Ferfar)\s*[:\-]\s*([A-Za-z0-9\-\/]+)"],
    "registration_number": [r"(?:Registration\s*No|Registration\s*Number|Dast\s*No)\s*[:\-]\s*([A-Za-z0-9\-\/]+)"],
    "registration_date": [r"(?:Registration\s*Date|Date\s*of\s*Registration)\s*[:\-]\s*(\d{4}-\d{2}-\d{2}|\d{2}[/-]\d{2}[/-]\d{4})"],
    "remarks": [r"Remarks\s*[:\-]\s*(.*)"]
}


class FieldExtractor:
    def extract_fields(self, ocr_result: OCRResult) -> List[Dict[str, Any]]:
        text = ocr_result.raw_text
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        extracted_list: List[Dict[str, Any]] = []

        # Find matching tokens to bind bounding boxes
        token_map: Dict[str, OCRToken] = {}
        for token in ocr_result.tokens:
            for field in FIELD_PATTERNS.keys():
                if field.replace("_", " ") in token.text.lower() or field in token.text.lower():
                    token_map[field] = token

        for field_name, patterns in FIELD_PATTERNS.items():
            extracted_val = None
            source_snippet = None

            for pat in patterns:
                match = re.search(pat, text, re.IGNORECASE)
                if match:
                    extracted_val = match.group(1).strip() if match.groups() else match.group(0).strip()
                    # Clean boundary characters
                    extracted_val = extracted_val.split("|")[0].split("\n")[0].strip()
                    source_snippet = match.group(0).strip()
                    break

            # Fallbacks / Default values if not matched directly
            if not extracted_val and field_name == "area_unit":
                if "hectare" in text.lower():
                    extracted_val = "Hectares"
                elif "bigha" in text.lower():
                    extracted_val = "Bigha"
                elif "gunta" in text.lower():
                    extracted_val = "Guntas"
                elif "acre" in text.lower():
                    extracted_val = "Acres"

            # Token bounding box and confidence binding
            matching_token = token_map.get(field_name)
            token_conf = matching_token.confidence if matching_token else 0.88
            bounding_box = matching_token.box if matching_token else None

            # If survey number has smudge or '?'
            if field_name == "survey_number" and extracted_val and "?" in extracted_val:
                token_conf = 0.52

            confidence = calculate_field_confidence(
                field_name=field_name,
                extracted_value=extracted_val,
                token_confidence=token_conf,
                has_anchor=bool(source_snippet)
            )

            # Assign synthetic fallback bounding box if not present
            if not bounding_box:
                bounding_box = {
                    "x": 10,
                    "y": 10 + (len(extracted_list) * 5),
                    "w": 40,
                    "h": 3,
                    "page": 1
                }

            extracted_list.append({
                "field": field_name,
                "value": extracted_val,
                "confidence": confidence,
                "source_text": source_snippet or (f"{field_name}: {extracted_val}" if extracted_val else None),
                "verified": False,
                "bounding_box": bounding_box
            })

        return extracted_list
