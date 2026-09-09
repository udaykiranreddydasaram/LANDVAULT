from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer, cast
from backend.app.api.deps import get_db
from backend.app.models.document import Document
from backend.app.models.land_record import LandRecord
from backend.app.models.verification_task import VerificationTask
from backend.app.models.validation_result import ValidationResult
from backend.app.models.land_record_field import LandRecordField
from backend.app.schemas.analytics import (
    AnalyticsDashboardData,
    MetricSummary,
    ConfidenceDistribution,
    RuleFailureStat,
    VillageDigitizationStat
)

router = APIRouter()


@router.get("/dashboard", response_model=AnalyticsDashboardData)
def get_analytics_dashboard(db: Session = Depends(get_db)):
    total_docs = db.query(Document).count()
    verified_recs = db.query(LandRecord).filter(LandRecord.is_verified == True).count()
    pending_tasks = db.query(VerificationTask).filter(VerificationTask.status == "PENDING").count()
    disputed_recs = db.query(LandRecord).filter(LandRecord.is_disputed == True).count()

    auto_verified_count = db.query(Document).filter(Document.status == "VERIFIED").count()
    auto_rate = round((auto_verified_count / total_docs * 100.0), 1) if total_docs > 0 else 0.0

    # Average confidence across all extracted fields
    avg_conf_query = db.query(func.avg(LandRecordField.confidence)).scalar()
    avg_conf = round(float(avg_conf_query), 2) if avg_conf_query is not None else 0.88

    # Confidence distribution
    high_count = db.query(LandRecordField).filter(LandRecordField.confidence >= 0.90).count()
    med_count = db.query(LandRecordField).filter(
        LandRecordField.confidence >= 0.70, LandRecordField.confidence < 0.90
    ).count()
    low_count = db.query(LandRecordField).filter(LandRecordField.confidence < 0.70).count()

    # Top rule failures
    failure_counts = db.query(
        ValidationResult.rule_code,
        ValidationResult.rule_name,
        func.count(ValidationResult.id).label("count")
    ).filter(
        ValidationResult.status == "FAILED"
    ).group_by(
        ValidationResult.rule_code, ValidationResult.rule_name
    ).order_by(
        func.count(ValidationResult.id).desc()
    ).limit(5).all()

    top_failures = [
        RuleFailureStat(
            rule_code=fc.rule_code,
            rule_name=fc.rule_name,
            failure_count=fc.count
        )
        for fc in failure_counts
    ]

    # Village statistics
    village_groups = db.query(
        LandRecord.village,
        LandRecord.district,
        func.count(LandRecord.id).label("total"),
        func.sum(cast(LandRecord.is_verified, Integer)).label("verified")
    ).group_by(LandRecord.village, LandRecord.district).limit(6).all()

    village_stats = []
    for vg in village_groups:
        total = vg.total or 1
        verif = vg.verified or 0
        village_stats.append(VillageDigitizationStat(
            village=vg.village,
            district=vg.district,
            total_records=total,
            verified_count=verif,
            completion_percentage=round((verif / total) * 100.0, 1)
        ))

    # Synthetic ingestion trend for Recharts
    trend = [
        {"day": "Mon", "ingested": 18, "verified": 14, "rejected": 1},
        {"day": "Tue", "ingested": 24, "verified": 20, "rejected": 2},
        {"day": "Wed", "ingested": 35, "verified": 31, "rejected": 1},
        {"day": "Thu", "ingested": 42, "verified": 38, "rejected": 3},
        {"day": "Fri", "ingested": 30, "verified": 27, "rejected": 0},
        {"day": "Sat", "ingested": 15, "verified": 14, "rejected": 1},
        {"day": "Sun", "ingested": 10, "verified": 10, "rejected": 0}
    ]

    return AnalyticsDashboardData(
        metrics=MetricSummary(
            total_documents=total_docs,
            verified_records=verified_recs,
            pending_verification=pending_tasks,
            disputed_records=disputed_recs,
            auto_verification_rate=auto_rate,
            average_confidence=avg_conf
        ),
        confidence_distribution=ConfidenceDistribution(
            high_count=high_count,
            medium_count=med_count,
            low_count=low_count
        ),
        top_rule_failures=top_failures,
        village_stats=village_stats,
        recent_ingestion_trend=trend
    )
