import {
  User,
  DocumentItem,
  DocumentDetail,
  VerificationTask,
  VerificationStudioDetail,
  LandRecord,
  GeoJSONFeatureCollection,
  AnalyticsDashboardData,
  AuditLogItem
} from '../types';

const API_BASE = 'http://localhost:8000/api/v1';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('landvault_token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  // Auth
  async login(username: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${API_BASE}/auth/login-json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Authentication failed' }));
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },

  async getCurrentUser(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch user profile');
    return res.json();
  },

  async seedUsers(): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/auth/seed-users`, {
      method: 'POST',
    });
    return res.json();
  },

  // Documents
  async listDocuments(statusFilter?: string): Promise<DocumentItem[]> {
    const url = new URL(`${API_BASE}/documents`);
    if (statusFilter && statusFilter !== 'ALL') {
      url.searchParams.set('status_filter', statusFilter);
    }
    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load documents');
    return res.json();
  },

  async getDocumentDetail(id: number): Promise<DocumentDetail> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load document details');
    return res.json();
  },

  async uploadDocument(
    file: File,
    documentType: string = 'Pattadar Passbook / ROR',
    allowDuplicate: boolean = false
  ): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    if (allowDuplicate) {
      formData.append('allow_duplicate', 'true');
    }

    const token = localStorage.getItem('landvault_token');
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Failed to upload document');
    }
    return res.json();
  },

  async reprocessDocument(id: number): Promise<DocumentDetail> {
    const res = await fetch(`${API_BASE}/documents/${id}/reprocess`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to reprocess document');
    return res.json();
  },

  // Verification
  async listVerificationTasks(statusFilter: string = 'PENDING'): Promise<VerificationTask[]> {
    const url = new URL(`${API_BASE}/verification/tasks`);
    if (statusFilter) url.searchParams.set('status_filter', statusFilter);
    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load verification tasks');
    return res.json();
  },

  async getVerificationStudioDetail(taskId: number): Promise<VerificationStudioDetail> {
    const res = await fetch(`${API_BASE}/verification/tasks/${taskId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load verification studio detail');
    return res.json();
  },

  async updateField(taskId: number, fieldName: string, value: string): Promise<any> {
    const res = await fetch(`${API_BASE}/verification/tasks/${taskId}/field`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ field_name: fieldName, value }),
    });
    if (!res.ok) throw new Error('Failed to update field');
    return res.json();
  },

  async updateBatchFields(taskId: number, fields: Record<string, string>): Promise<any> {
    const res = await fetch(`${API_BASE}/verification/tasks/${taskId}/batch-fields`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ fields }),
    });
    if (!res.ok) throw new Error('Failed to update fields and re-validate');
    return res.json();
  },

  async submitVerificationDecision(
    taskId: number,
    decision: 'APPROVE' | 'REJECT',
    notes?: string,
    rejectionReason?: string,
    editedFields?: Record<string, string>
  ): Promise<any> {
    const res = await fetch(`${API_BASE}/verification/tasks/${taskId}/decision`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        decision,
        notes,
        rejection_reason: rejectionReason,
        edited_fields: editedFields,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Decision submission failed' }));
      throw new Error(err.detail || 'Failed to submit decision');
    }
    return res.json();
  },

  // Land Records
  async listLandRecords(search?: string, village?: string): Promise<LandRecord[]> {
    const url = new URL(`${API_BASE}/land-records`);
    if (search) url.searchParams.set('search', search);
    if (village) url.searchParams.set('village', village);
    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load land records');
    return res.json();
  },

  async getLandRecordDetail(id: number): Promise<LandRecord> {
    const res = await fetch(`${API_BASE}/land-records/${id}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load land record');
    return res.json();
  },

  async getLandRecordCertificate(id: number): Promise<any> {
    const res = await fetch(`${API_BASE}/land-records/${id}/certificate`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load certificate');
    return res.json();
  },

  // GIS
  async getGISParcels(village?: string, statusFilter?: string): Promise<GeoJSONFeatureCollection> {
    const url = new URL(`${API_BASE}/gis/parcels`);
    if (village) url.searchParams.set('village', village);
    if (statusFilter && statusFilter !== 'ALL') url.searchParams.set('status_filter', statusFilter);
    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load GIS cadastral parcels');
    return res.json();
  },

  // Analytics
  async getAnalyticsDashboard(): Promise<AnalyticsDashboardData> {
    const res = await fetch(`${API_BASE}/analytics/dashboard`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load analytics dashboard');
    return res.json();
  },

  // Audit
  async getAuditLogs(actionFilter?: string): Promise<AuditLogItem[]> {
    const url = new URL(`${API_BASE}/audit/logs`);
    if (actionFilter) url.searchParams.set('action_filter', actionFilter);
    const res = await fetch(url.toString(), {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to load audit trail');
    return res.json();
  },

  // Adapters
  async verifyDILRMP(surveyNo: string): Promise<any> {
    const res = await fetch(`${API_BASE}/adapters/dilrmp/verify/${encodeURIComponent(surveyNo)}`);
    return res.json();
  },

  async syncLRMS(recordId: string, owner: string, survey: string, area: number): Promise<any> {
    const res = await fetch(`${API_BASE}/adapters/lrms/sync-mutation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        record_identifier: recordId,
        landowner_name: owner,
        survey_number: survey,
        land_area: area,
        area_unit: 'Acres',
      }),
    });
    return res.json();
  },
};
