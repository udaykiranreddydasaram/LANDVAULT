export type UserRole = 'admin' | 'verifier' | 'viewer';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  department?: string;
  is_active: boolean;
}

export interface BoundingBox {
  x: number; // percentage 0-100
  y: number; // percentage 0-100
  w: number; // percentage 0-100
  h: number; // percentage 0-100
  page?: number;
}

export interface ExtractedField {
  field: string;
  value: string | null;
  confidence: number;
  source_text: string | null;
  verified: boolean;
  bounding_box?: BoundingBox | null;
}

export interface ValidationResult {
  id?: number;
  rule_code: string;
  rule_name: string;
  severity: 'CRITICAL' | 'ERROR' | 'WARNING' | 'INFO';
  status: 'PASSED' | 'FAILED';
  target_field?: string | null;
  message: string;
  details?: Record<string, any>;
}

export interface DocumentItem {
  id: number;
  file_name: string;
  file_path: string;
  file_hash: string;
  file_size_bytes: number;
  mime_type: string;
  document_type: string;
  status: 'UPLOADED' | 'PROCESSING' | 'EXTRACTED' | 'VALIDATION_FAILED' | 'REQUIRES_VERIFICATION' | 'VERIFIED' | 'REJECTED';
  ocr_provider: string;
  uploaded_by_id?: number | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentDetail extends DocumentItem {
  raw_ocr_text?: string | null;
  fields: ExtractedField[];
  validation_results: ValidationResult[];
  verification_task_id?: number | null;
  land_record_id?: number | null;
}

export interface VerificationTask {
  id: number;
  document_id: number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'PENDING' | 'IN_REVIEW' | 'APPROVED' | 'REJECTED';
  assigned_to_id?: number | null;
  rejection_reason?: string | null;
  notes?: string | null;
  created_at: string;
  resolved_at?: string | null;
  file_name?: string;
  village?: string;
  survey_number?: string;
  overall_confidence?: number;
}

export interface VerificationStudioDetail {
  task: VerificationTask;
  document_id: number;
  file_name: string;
  file_path: string;
  mime_type: string;
  raw_ocr_text?: string | null;
  fields: ExtractedField[];
  validation_results: ValidationResult[];
}

export interface LandRecord {
  id: number;
  document_id: number;
  record_identifier: string;
  state: string;
  district: string;
  mandal_tehsil: string;
  village: string;
  landowner_name: string;
  survey_number: string;
  khasra_number?: string | null;
  khata_number?: string | null;
  plot_number?: string | null;
  land_area: number;
  area_unit: string;
  land_classification: string;
  ownership_type: string;
  mutation_number?: string | null;
  registration_number?: string | null;
  registration_date?: string | null;
  remarks?: string | null;
  overall_confidence: number;
  is_verified: boolean;
  is_disputed: boolean;
  verified_by_id?: number | null;
  verified_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface GISParcelProperties {
  id: number;
  land_record_id: number;
  survey_number: string;
  village: string;
  mandal_tehsil?: string | null;
  district: string;
  state: string;
  landowner_name?: string | null;
  land_area?: number | null;
  area_unit?: string;
  khata_number?: string | null;
  status: 'VERIFIED' | 'PENDING_REVIEW' | 'DISPUTED';
  overall_confidence?: number;
}

export interface GeoJSONFeature {
  type: 'Feature';
  id: number;
  geometry: {
    type: 'Polygon';
    coordinates: number[][][];
  };
  properties: GISParcelProperties;
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

export interface MetricSummary {
  total_documents: number;
  verified_records: number;
  pending_verification: number;
  disputed_records: number;
  auto_verification_rate: number;
  average_confidence: number;
}

export interface AnalyticsDashboardData {
  metrics: MetricSummary;
  confidence_distribution: {
    high_count: number;
    medium_count: number;
    low_count: number;
  };
  top_rule_failures: {
    rule_code: string;
    rule_name: string;
    failure_count: number;
  }[];
  village_stats: {
    village: string;
    district: string;
    total_records: number;
    verified_count: number;
    completion_percentage: number;
  }[];
  recent_ingestion_trend: {
    day: string;
    ingested: number;
    verified: number;
    rejected: number;
  }[];
}

export interface AuditLogItem {
  id: number;
  entity_name: string;
  entity_id: string;
  action: string;
  performed_by: string;
  performed_by_role: string;
  old_values?: any;
  new_values?: any;
  ip_address: string;
  timestamp: string;
}
