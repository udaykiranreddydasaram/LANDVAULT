import re
from typing import Optional, Dict, Any


def get_confidence_category(confidence: float) -> str:
    """
    Returns:
        HIGH: 90 - 100%
        MEDIUM: 70 - 89%
        LOW: 0 - 69%
    """
    pct = confidence * 100.0
    if pct >= 90.0:
        return "HIGH"
    elif pct >= 70.0:
        return "MEDIUM"
    else:
        return "LOW"


def calculate_field_confidence(
    field_name: str,
    extracted_value: Optional[str],
    token_confidence: float = 0.90,
    has_anchor: bool = True
) -> float:
    """
    Calculates multi-factor confidence for an extracted land record field:
    Confidence = 0.40 * Token_Confidence + 0.35 * Pattern_Score + 0.25 * Anchor_Score
    """
    if extracted_value is None or str(extracted_value).strip() == "" or str(extracted_value).strip() == "?":
        return 0.20

    val_str = str(extracted_value).strip()

    # Pattern score evaluation
    pattern_score = 1.0
    if field_name == "survey_number":
        # Check if contains ? or smudge indicators
        if "?" in val_str or "smudge" in val_str.lower() or "unclear" in val_str.lower():
            pattern_score = 0.20
        elif re.match(r"^\d{1,4}(/\d{1,4})?([A-Za-z]+)?$", val_str):
            pattern_score = 1.0
        else:
            pattern_score = 0.60
    elif field_name == "land_area":
        try:
            num = float(re.sub(r"[^\d.]", "", val_str))
            pattern_score = 1.0 if num > 0 else 0.10
        except Exception:
            pattern_score = 0.30
    elif field_name == "registration_date":
        if re.match(r"^\d{4}-\d{2}-\d{2}$", val_str):
            pattern_score = 1.0
        else:
            pattern_score = 0.50
    elif field_name in ["state", "district", "village", "mandal_tehsil"]:
        pattern_score = 1.0 if len(val_str) > 2 and not any(c.isdigit() for c in val_str) else 0.50

    anchor_score = 1.0 if has_anchor else 0.50

    total_conf = (0.40 * token_confidence) + (0.35 * pattern_score) + (0.25 * anchor_score)
    return round(min(max(total_conf, 0.0), 1.0), 2)
