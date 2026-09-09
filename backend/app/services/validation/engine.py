from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from backend.app.services.validation.rules import (
    RuleResult,
    check_mandatory_fields,
    check_land_area,
    check_survey_number,
    check_area_unit,
    check_administrative_hierarchy,
    check_mutation_ownership_consistency
)
from backend.app.services.duplicate.detector import DuplicateDetector


class ValidationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.dupe_detector = DuplicateDetector(db)

    def validate_fields(
        self,
        fields_dict: Dict[str, Any],
        overall_confidence: float,
        exclude_record_id: int = None
    ) -> Tuple[List[RuleResult], bool, bool]:
        """
        Executes all validation rules against extracted fields.
        Returns:
            - results: List[RuleResult]
            - requires_verification: bool (True if confidence < 0.70 OR any CRITICAL/ERROR failed)
            - is_disputed: bool (True if duplicate survey collision found)
        """
        results: List[RuleResult] = []

        # 1. Mandatory Fields
        results.extend(check_mandatory_fields(fields_dict))

        # 2. Land Area > 0
        results.append(check_land_area(fields_dict))

        # 3. Survey Number Format
        results.append(check_survey_number(fields_dict))

        # 4. Area Unit Legality
        results.append(check_area_unit(fields_dict))

        # 5. Administrative Hierarchy
        results.append(check_administrative_hierarchy(fields_dict))

        # 6. Mutation Consistency
        results.append(check_mutation_ownership_consistency(fields_dict))

        # 7. Cadastral Survey Collision (Duplicate Check)
        dupe_result, is_disputed = self.dupe_detector.check_duplicate_cadastral_survey(
            survey_number=str(fields_dict.get("survey_number", "")),
            village=str(fields_dict.get("village", "")),
            district=str(fields_dict.get("district", "")),
            state=str(fields_dict.get("state", "")),
            exclude_record_id=exclude_record_id
        )
        results.append(dupe_result)

        # 8. Confidence-based human verification check (Threshold: 70%)
        has_critical_failure = any(
            r.status == "FAILED" and r.severity in ["CRITICAL", "ERROR"] 
            for r in results
        )
        is_low_confidence = overall_confidence < 0.70

        if is_low_confidence:
            results.append(RuleResult(
                rule_code="VAL_CONFIDENCE_THRESHOLD",
                rule_name="AI Confidence Threshold Evaluation",
                severity="WARNING",
                passed=False,
                message=f"Overall extraction confidence ({int(overall_confidence * 100)}%) is below high-trust threshold (70%). Routed to human verification.",
                details={"confidence": overall_confidence}
            ))
        else:
            results.append(RuleResult(
                rule_code="VAL_CONFIDENCE_THRESHOLD",
                rule_name="AI Confidence Threshold Evaluation",
                severity="INFO",
                passed=True,
                message=f"Overall extraction confidence ({int(overall_confidence * 100)}%) satisfies automatic validation criteria.",
                details={"confidence": overall_confidence}
            ))

        requires_verification = has_critical_failure or is_low_confidence or is_disputed

        return results, requires_verification, is_disputed
