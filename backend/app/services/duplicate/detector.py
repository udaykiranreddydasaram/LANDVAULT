import hashlib
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from backend.app.models.document import Document
from backend.app.models.land_record import LandRecord
from backend.app.services.validation.rules import RuleResult


def calculate_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


class DuplicateDetector:
    def __init__(self, db: Session):
        self.db = db

    def check_duplicate_document(self, file_hash: str, exclude_doc_id: Optional[int] = None) -> Optional[RuleResult]:
        query = self.db.query(Document).filter(Document.file_hash == file_hash)
        if exclude_doc_id:
            query = query.filter(Document.id != exclude_doc_id)
        existing = query.first()

        if existing:
            return RuleResult(
                rule_code="VAL_DUPLICATE_DOCUMENT",
                rule_name="Duplicate Document Content Hash",
                severity="CRITICAL",
                passed=False,
                message=f"Duplicate document detected! Matches previously uploaded document ID #{existing.id} ({existing.file_name}).",
                details={"existing_document_id": existing.id, "file_name": existing.file_name}
            )
        return RuleResult(
            rule_code="VAL_DUPLICATE_DOCUMENT",
            rule_name="Duplicate Document Content Hash",
            severity="CRITICAL",
            passed=True,
            message="Document content hash is unique."
        )

    def check_duplicate_cadastral_survey(
        self,
        survey_number: str,
        village: str,
        district: str,
        state: str,
        exclude_record_id: Optional[int] = None
    ) -> Tuple[RuleResult, bool]:
        """
        Checks if the survey number has already been registered in the same village.
        Returns (RuleResult, is_disputed_flag)
        """
        if not (survey_number and village and district and state):
            return RuleResult(
                rule_code="VAL_DUPLICATE_SURVEY",
                rule_name="Duplicate Cadastral Survey Check",
                severity="WARNING",
                passed=True,
                message="Cadastral duplicate check skipped due to incomplete location."
            ), False

        query = self.db.query(LandRecord).filter(
            LandRecord.survey_number == survey_number.strip(),
            LandRecord.village.ilike(village.strip()),
            LandRecord.district.ilike(district.strip()),
            LandRecord.state.ilike(state.strip()),
            LandRecord.is_verified == True
        )
        if exclude_record_id:
            query = query.filter(LandRecord.id != exclude_record_id)

        collision = query.first()
        if collision:
            return RuleResult(
                rule_code="VAL_DUPLICATE_SURVEY",
                rule_name="Duplicate Cadastral Survey Check",
                severity="WARNING",
                passed=False,
                message=f"Cadastral Collision Warning: Survey No '{survey_number}' is already registered to '{collision.landowner_name}' in village '{village}' (Record #{collision.record_identifier}).",
                target_field="survey_number",
                details={"existing_record_id": collision.id, "existing_owner": collision.landowner_name}
            ), True

        return RuleResult(
            rule_code="VAL_DUPLICATE_SURVEY",
            rule_name="Duplicate Cadastral Survey Check",
            severity="WARNING",
            passed=True,
            message=f"Survey No '{survey_number}' is unique in village '{village}'.",
            target_field="survey_number"
        ), False
