import re
from typing import Dict, Any, List, Optional
from backend.app.services.validation.master_data import (
    validate_hierarchy, 
    VALID_AREA_UNITS, 
    INDIAN_ADMIN_HIERARCHY
)

MANDATORY_FIELDS = [
    "state",
    "district",
    "mandal_tehsil",
    "village",
    "landowner_name",
    "survey_number",
    "land_area",
    "area_unit"
]

SURVEY_NUMBER_REGEX = re.compile(r"^\d{1,4}(\s*[/\\-]\s*(\d{1,4}|[A-Za-z]+))?(\s*[/\\-]\s*[A-Za-z0-9]+)?$")


class RuleResult:
    def __init__(
        self,
        rule_code: str,
        rule_name: str,
        severity: str, # CRITICAL, ERROR, WARNING, INFO
        passed: bool,
        message: str,
        target_field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.rule_code = rule_code
        self.rule_name = rule_name
        self.severity = severity
        self.passed = passed
        self.status = "PASSED" if passed else "FAILED"
        self.message = message
        self.target_field = target_field
        self.details = details or {}


def check_mandatory_fields(field_values: Dict[str, Any]) -> List[RuleResult]:
    results = []
    missing = []
    for mf in MANDATORY_FIELDS:
        val = field_values.get(mf)
        if val is None or str(val).strip() == "" or str(val).strip().lower() == "null" or str(val).strip() == "?":
            missing.append(mf)
            results.append(RuleResult(
                rule_code="VAL_MANDATORY_FIELD",
                rule_name="Mandatory Field Non-Empty",
                severity="CRITICAL",
                passed=False,
                message=f"Mandatory field '{mf}' is missing or unreadable.",
                target_field=mf
            ))
            
    if not missing:
        results.append(RuleResult(
            rule_code="VAL_MANDATORY_FIELD",
            rule_name="Mandatory Field Non-Empty",
            severity="CRITICAL",
            passed=True,
            message="All mandatory land record fields are present."
        ))
    return results


def check_land_area(field_values: Dict[str, Any]) -> RuleResult:
    area_val = field_values.get("land_area")
    if area_val is None or str(area_val).strip() == "":
        return RuleResult(
            rule_code="VAL_AREA_POS",
            rule_name="Positive Land Area",
            severity="ERROR",
            passed=False,
            message="Land area is empty.",
            target_field="land_area"
        )
    try:
        clean_num = re.sub(r"[^\d.-]", "", str(area_val))
        val = float(clean_num)
        if val <= 0:
            return RuleResult(
                rule_code="VAL_AREA_POS",
                rule_name="Positive Land Area",
                severity="ERROR",
                passed=False,
                message=f"Land area must be greater than zero. Extracted value: {val}",
                target_field="land_area",
                details={"value": val}
            )
        return RuleResult(
            rule_code="VAL_AREA_POS",
            rule_name="Positive Land Area",
            severity="ERROR",
            passed=True,
            message=f"Land area is valid: {val}",
            target_field="land_area",
            details={"value": val}
        )
    except Exception as e:
        return RuleResult(
            rule_code="VAL_AREA_POS",
            rule_name="Positive Land Area",
            severity="ERROR",
            passed=False,
            message=f"Could not parse numeric land area: '{area_val}'",
            target_field="land_area"
        )


def check_survey_number(field_values: Dict[str, Any]) -> RuleResult:
    survey_val = field_values.get("survey_number")
    if not survey_val or str(survey_val).strip() in ["", "?", "null", "undefined"]:
        return RuleResult(
            rule_code="VAL_SURVEY_FMT",
            rule_name="Survey Number Format",
            severity="ERROR",
            passed=False,
            message="Survey number is empty or contains OCR smudge placeholders.",
            target_field="survey_number"
        )
    
    clean_val = str(survey_val).strip()
    if SURVEY_NUMBER_REGEX.match(clean_val):
        return RuleResult(
            rule_code="VAL_SURVEY_FMT",
            rule_name="Survey Number Format",
            severity="ERROR",
            passed=True,
            message=f"Survey number '{clean_val}' conforms to Indian cadastral syntax.",
            target_field="survey_number"
        )
    else:
        return RuleResult(
            rule_code="VAL_SURVEY_FMT",
            rule_name="Survey Number Format",
            severity="ERROR",
            passed=False,
            message=f"Survey number '{clean_val}' does not match standard cadastral format (e.g. 124, 124/2, 45-B).",
            target_field="survey_number",
            details={"raw_value": clean_val}
        )


def check_area_unit(field_values: Dict[str, Any]) -> RuleResult:
    unit_val = field_values.get("area_unit")
    if not unit_val or str(unit_val).strip() == "":
        return RuleResult(
            rule_code="VAL_AREA_UNIT",
            rule_name="Area Unit Legality",
            severity="WARNING",
            passed=False,
            message="Area unit is not specified.",
            target_field="area_unit"
        )
    
    clean_unit = str(unit_val).strip().title()
    matched = any(u.lower() == clean_unit.lower() for u in VALID_AREA_UNITS)
    if matched:
        return RuleResult(
            rule_code="VAL_AREA_UNIT",
            rule_name="Area Unit Legality",
            severity="WARNING",
            passed=True,
            message=f"Area unit '{clean_unit}' is recognized.",
            target_field="area_unit"
        )
    else:
        return RuleResult(
            rule_code="VAL_AREA_UNIT",
            rule_name="Area Unit Legality",
            severity="WARNING",
            passed=False,
            message=f"Area unit '{unit_val}' is not in the legal standard units whitelist ({', '.join(VALID_AREA_UNITS[:5])}...).",
            target_field="area_unit"
        )


def check_administrative_hierarchy(field_values: Dict[str, Any]) -> RuleResult:
    state = str(field_values.get("state", "")).strip()
    district = str(field_values.get("district", "")).strip()
    mandal = str(field_values.get("mandal_tehsil", "")).strip()
    village = str(field_values.get("village", "")).strip()
    
    if not (state and district and mandal and village):
        return RuleResult(
            rule_code="VAL_GEO_HIERARCHY",
            rule_name="Administrative Geographic Hierarchy",
            severity="CRITICAL",
            passed=False,
            message="Incomplete administrative location fields; hierarchy validation skipped.",
            target_field="village"
        )
        
    is_valid = validate_hierarchy(state, district, mandal, village)
    if is_valid:
        return RuleResult(
            rule_code="VAL_GEO_HIERARCHY",
            rule_name="Administrative Geographic Hierarchy",
            severity="CRITICAL",
            passed=True,
            message=f"Verified valid administrative hierarchy: {village} -> {mandal} -> {district} -> {state}.",
            target_field="village"
        )
    else:
        return RuleResult(
            rule_code="VAL_GEO_HIERARCHY",
            rule_name="Administrative Geographic Hierarchy",
            severity="CRITICAL",
            passed=False,
            message=f"Geographic mismatch: Village '{village}' does not map to Mandal '{mandal}', District '{district}', State '{state}'.",
            target_field="village",
            details={"state": state, "district": district, "mandal": mandal, "village": village}
        )


def check_mutation_ownership_consistency(field_values: Dict[str, Any]) -> RuleResult:
    owner = field_values.get("landowner_name")
    mutation_no = field_values.get("mutation_number")
    reg_no = field_values.get("registration_number")
    
    if mutation_no and not reg_no:
        return RuleResult(
            rule_code="VAL_OWNER_MUTATION",
            rule_name="Mutation & Registration Consistency",
            severity="WARNING",
            passed=False,
            message=f"Mutation number '{mutation_no}' present without prior Registration Number reference.",
            target_field="mutation_number"
        )
        
    return RuleResult(
        rule_code="VAL_OWNER_MUTATION",
        rule_name="Mutation & Registration Consistency",
        severity="INFO",
        passed=True,
        message="Ownership and mutation references appear consistent.",
        target_field="landowner_name"
    )
