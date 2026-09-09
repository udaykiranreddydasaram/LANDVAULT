from typing import List, Dict, Any
from pydantic import BaseModel


class MetricSummary(BaseModel):
    total_documents: int
    verified_records: int
    pending_verification: int
    disputed_records: int
    auto_verification_rate: float
    average_confidence: float


class ConfidenceDistribution(BaseModel):
    high_count: int
    medium_count: int
    low_count: int


class RuleFailureStat(BaseModel):
    rule_code: str
    rule_name: str
    failure_count: int


class VillageDigitizationStat(BaseModel):
    village: str
    district: str
    total_records: int
    verified_count: int
    completion_percentage: float


class AnalyticsDashboardData(BaseModel):
    metrics: MetricSummary
    confidence_distribution: ConfidenceDistribution
    top_rule_failures: List[RuleFailureStat]
    village_stats: List[VillageDigitizationStat]
    recent_ingestion_trend: List[Dict[str, Any]]
