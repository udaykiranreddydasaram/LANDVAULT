import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Save,
  Check,
  ShieldCheck,
  FileText,
  Sparkles,
  Info,
  RefreshCw,
} from 'lucide-react';
import { VerificationStudioDetail, ExtractedField } from '../types';
import { api } from '../services/api';

interface VerificationStudioPageProps {
  taskId: number;
  onBack: () => void;
  onVerifiedSuccess: () => void;
}

export const VerificationStudioPage: React.FC<VerificationStudioPageProps> = ({
  taskId,
  onBack,
  onVerifiedSuccess,
}) => {
  const [detail, setDetail] = useState<VerificationStudioDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeField, setActiveField] = useState<string | null>('survey_number');
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({});
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [rejectionModalOpen, setRejectionModalOpen] = useState<boolean>(false);
  const [rejectionReason, setRejectionReason] = useState<string>('');
  const [notes, setNotes] = useState<string>('Verified against revenue paper stamp records.');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    async function loadStudioData() {
      try {
        setLoading(true);
        const data = await api.getVerificationStudioDetail(taskId);
        setDetail(data);

        // Pre-fill form state
        const initialVals: Record<string, string> = {};
        data.fields.forEach((f) => {
          initialVals[f.field] = f.value || '';
        });
        setFieldValues(initialVals);
      } catch (err: any) {
        setMessage({ type: 'error', text: err.message || 'Failed to load verification task' });
      } finally {
        setLoading(false);
      }
    }
    loadStudioData();
  }, [taskId]);

  const handleFieldChange = (fieldName: string, newVal: string) => {
    setFieldValues((prev) => ({ ...prev, [fieldName]: newVal }));
  };

  // Immediate single-field update & re-validation against backend
  const handleSaveField = async (fieldName: string) => {
    try {
      await api.updateField(taskId, fieldName, fieldValues[fieldName]);
      // Reload studio data to refresh validation errors
      const refreshed = await api.getVerificationStudioDetail(taskId);
      setDetail(refreshed);
      setMessage({ type: 'success', text: `Field "${fieldName}" updated & re-validated!` });
      setTimeout(() => setMessage(null), 2500);
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message });
    }
  };

  const [validating, setValidating] = useState<boolean>(false);

  // Full batch update & re-run of all 6 validation rules
  const handleRerunValidation = async () => {
    try {
      setValidating(true);
      await api.updateBatchFields(taskId, fieldValues);
      const refreshed = await api.getVerificationStudioDetail(taskId);
      setDetail(refreshed);
      const fails = refreshed.validation_results.filter((vr) => vr.status === 'FAILED');
      if (fails.length === 0) {
        setMessage({ type: 'success', text: 'Validation engine re-executed: All rules PASSED! Record ready for approval.' });
      } else {
        setMessage({ type: 'error', text: `Validation engine re-executed: ${fails.length} exception(s) remain.` });
      }
      setTimeout(() => setMessage(null), 3500);
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Validation failed' });
    } finally {
      setValidating(false);
    }
  };

  const handleApprove = async () => {
    try {
      setIsSubmitting(true);
      await api.submitVerificationDecision(
        taskId,
        'APPROVE',
        notes,
        undefined,
        fieldValues
      );
      setMessage({ type: 'success', text: 'Land record officially verified and promoted to GIS cadastre!' });
      setTimeout(() => {
        onVerifiedSuccess();
      }, 1200);
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Approval failed' });
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!rejectionReason) {
      alert('Please provide a reason for rejecting the document.');
      return;
    }
    try {
      setIsSubmitting(true);
      await api.submitVerificationDecision(
        taskId,
        'REJECT',
        notes,
        rejectionReason,
        fieldValues
      );
      setRejectionModalOpen(false);
      onVerifiedSuccess();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Rejection failed' });
      setIsSubmitting(false);
    }
  };

  if (loading || !detail) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-400">Loading Human Verification Studio...</p>
        </div>
      </div>
    );
  }

  // Determine image source URL
  let imageSrc = `http://localhost:8000/samples/Sample_Patta_Deed_Telangana_Smudged_1988.png`;
  if (detail.file_name.includes('Clean')) {
    imageSrc = `http://localhost:8000/samples/Sample_Patta_Deed_Telangana_Clean.png`;
  } else if (detail.file_name.includes('Maharashtra') || detail.file_name.includes('7_12')) {
    imageSrc = `http://localhost:8000/samples/Sample_7_12_Extract_Maharashtra.png`;
  }

  // Active validation failures
  const failures = detail.validation_results.filter((vr) => vr.status === 'FAILED');

  // Helper for confidence badge
  const renderConfidenceBadge = (confidence: number) => {
    const pct = Math.round(confidence * 100);
    if (pct >= 90) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
          {pct}% HIGH
        </span>
      );
    } else if (pct >= 70) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
          {pct}% MED
        </span>
      );
    } else {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 animate-pulse">
          {pct}% LOW - SMUDGE
        </span>
      );
    }
  };

  return (
    <div className="space-y-4">
      {/* Studio Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 glass-card p-4 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-extrabold text-white">Verification Studio</span>
              <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono font-bold border border-amber-500/30">
                TASK #{detail.task.id}
              </span>
              <span className="text-xs text-slate-400">({detail.file_name})</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Interactive split-screen audit: Hover or edit any field to locate and verify with original historical deed.
            </p>
          </div>
        </div>

        {/* Global actions */}
        <div className="flex items-center gap-2 self-end sm:self-auto">
          <button
            onClick={handleRerunValidation}
            disabled={validating || isSubmitting}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition flex items-center gap-1.5"
            title="Re-run all validation rules against current field values"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${validating ? 'animate-spin text-emerald-400' : ''}`} />
            <span>{validating ? 'Re-validating...' : 'Re-run Validation'}</span>
          </button>
          <button
            onClick={() => setRejectionModalOpen(true)}
            disabled={isSubmitting}
            className="px-3.5 py-2 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-500/40 text-xs font-semibold transition flex items-center gap-1.5"
          >
            <XCircle className="w-4 h-4" />
            Reject Record
          </button>
          <button
            onClick={handleApprove}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white text-xs font-bold shadow-lg shadow-emerald-950/40 transition flex items-center gap-1.5"
          >
            <CheckCircle className="w-4 h-4" />
            {isSubmitting ? 'Promoting...' : 'Approve & Promoted to Cadastre'}
          </button>
        </div>
      </div>

      {/* Toast Alert */}
      {message && (
        <div
          className={`p-3 rounded-xl border text-xs flex items-center justify-between ${
            message.type === 'success'
              ? 'bg-emerald-950/50 text-emerald-200 border-emerald-500/40'
              : 'bg-rose-950/50 text-rose-200 border-rose-500/40'
          }`}
        >
          <span>{message.text}</span>
          <button onClick={() => setMessage(null)} className="text-slate-400 hover:text-white font-bold ml-2">
            ×
          </button>
        </div>
      )}

      {/* Split-Screen Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-[650px]">
        {/* LEFT PANE: Interactive Document Canvas with Bounding Box Overlays (5 cols) */}
        <div className="lg:col-span-5 glass-card rounded-2xl border border-slate-800 flex flex-col overflow-hidden">
          {/* Canvas Controls Header */}
          <div className="p-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-300 flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-400" />
              Scanned Legacy Artifact
            </span>
            <div className="flex items-center gap-1 bg-slate-800/80 rounded-lg p-1">
              <button
                onClick={() => setZoomLevel((z) => Math.max(z - 0.2, 0.6))}
                className="p-1 hover:bg-slate-700 rounded text-slate-300"
                title="Zoom Out"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <span className="px-2 font-mono text-[11px] text-slate-400">{Math.round(zoomLevel * 100)}%</span>
              <button
                onClick={() => setZoomLevel((z) => Math.min(z + 0.2, 2.0))}
                className="p-1 hover:bg-slate-700 rounded text-slate-300"
                title="Zoom In"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setZoomLevel(1)}
                className="p-1 hover:bg-slate-700 rounded text-slate-300 ml-1"
                title="Reset Zoom"
              >
                <Maximize2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Canvas Viewport */}
          <div className="relative flex-1 overflow-auto bg-slate-950/80 p-4 flex items-center justify-center">
            <div
              className="relative shadow-2xl transition-transform duration-150 origin-top-left"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              <img
                src={imageSrc}
                alt="Original Scanned Deed"
                className="max-w-[460px] w-full rounded border border-slate-700 select-none pointer-events-none"
              />

              {/* SVG Bounding Boxes Overlay */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                {detail.fields.map((f) => {
                  if (!f.bounding_box) return null;
                  const isFocused = activeField === f.field;
                  const isLowConf = f.confidence < 0.70;

                  return (
                    <g key={f.field}>
                      <rect
                        x={`${f.bounding_box.x}%`}
                        y={`${f.bounding_box.y}%`}
                        width={`${f.bounding_box.w}%`}
                        height={`${f.bounding_box.h}%`}
                        fill={
                          isFocused
                            ? isLowConf
                              ? 'rgba(239, 68, 68, 0.35)'
                              : 'rgba(16, 185, 129, 0.35)'
                            : isLowConf
                            ? 'rgba(245, 158, 11, 0.15)'
                            : 'transparent'
                        }
                        stroke={
                          isFocused
                            ? isLowConf
                              ? '#ef4444'
                              : '#10b981'
                            : isLowConf
                            ? '#f59e0b'
                            : 'rgba(255, 255, 255, 0.15)'
                        }
                        strokeWidth={isFocused ? 2.5 : 1}
                        strokeDasharray={isLowConf && !isFocused ? '3,3' : 'none'}
                        className={`transition-all duration-200 ${isFocused ? 'animate-pulse' : ''}`}
                      />
                      {isFocused && (
                        <text
                          x={`${f.bounding_box.x}%`}
                          y={`${Math.max(f.bounding_box.y - 1.5, 3)}%`}
                          fill={isLowConf ? '#fca5a5' : '#6ee7b7'}
                          fontSize="9"
                          fontWeight="bold"
                          fontFamily="sans-serif"
                        >
                          {f.field.replace('_', ' ').toUpperCase()}
                        </text>
                      )}
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>
        </div>

        {/* RIGHT PANE: Field-by-Field Inline Editor & Live Validation Engine (7 cols) */}
        <div className="lg:col-span-7 glass-card rounded-2xl border border-slate-800 p-6 flex flex-col justify-between space-y-4 overflow-hidden">
          {/* Validation Engine Exceptions Banner */}
          {failures.length > 0 ? (
            <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/40 space-y-1.5">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-300">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Rule Engine Exceptions Detected ({failures.length})</span>
              </div>
              <ul className="text-[11px] text-amber-200/80 space-y-1 pl-6 list-disc">
                {failures.map((fail, i) => (
                  <li key={i}>
                    <span className="font-semibold text-amber-300">[{fail.rule_code}]: </span>
                    {fail.message}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/40 flex items-center gap-2 text-xs text-emerald-300 font-semibold">
              <Check className="w-4 h-4 text-emerald-400" />
              <span>All validation rules passing. Ready for cadastral publication.</span>
            </div>
          )}

          {/* Form Scrollable Area */}
          <div className="overflow-y-auto max-h-[500px] pr-2 space-y-3.5">
            {detail.fields.map((f) => {
              const isActive = activeField === f.field;
              const hasFailure = failures.some((vr) => vr.target_field === f.field);

              return (
                <div
                  key={f.field}
                  onMouseEnter={() => setActiveField(f.field)}
                  className={`p-3.5 rounded-xl border transition-all ${
                    isActive
                      ? hasFailure
                        ? 'border-rose-500/60 bg-rose-950/20 shadow-sm'
                        : 'border-emerald-500/60 bg-emerald-950/20 shadow-sm'
                      : hasFailure
                      ? 'border-amber-500/40 bg-amber-950/10'
                      : 'border-slate-800 bg-slate-900/50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-bold text-slate-200 uppercase tracking-wide flex items-center gap-2">
                      {f.field.replace('_', ' ')}
                      {f.field === 'survey_number' && (
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 font-mono">
                          KEY CADASTRAL
                        </span>
                      )}
                    </label>

                    <div className="flex items-center gap-2">
                      {renderConfidenceBadge(f.confidence)}
                      {f.verified && (
                        <span className="text-[10px] text-emerald-400 flex items-center gap-1 font-semibold">
                          <Check className="w-3 h-3" /> Verified
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={fieldValues[f.field] ?? ''}
                      onFocus={() => setActiveField(f.field)}
                      onChange={(e) => handleFieldChange(f.field, e.target.value)}
                      placeholder={`Enter ${f.field.replace('_', ' ')}`}
                      className={`flex-1 bg-slate-950 border rounded-lg px-3 py-2 text-xs text-slate-100 font-mono focus:outline-none ${
                        hasFailure
                          ? 'border-rose-500/70 focus:border-rose-400'
                          : 'border-slate-700 focus:border-emerald-500'
                      }`}
                    />
                    <button
                      onClick={() => handleSaveField(f.field)}
                      title="Update & Re-validate"
                      className="px-2.5 py-2 rounded-lg bg-slate-800 hover:bg-emerald-600 text-slate-300 hover:text-white transition text-xs flex items-center gap-1"
                    >
                      <Save className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {f.source_text && (
                    <div className="text-[10px] text-slate-400 mt-1 font-mono flex items-center gap-1">
                      <span className="text-slate-400">OCR snippet:</span>
                      <span className="truncate italic">"{f.source_text}"</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Bottom Notes & Actions */}
          <div className="pt-3 border-t border-slate-800 space-y-2">
            <label className="text-xs font-semibold text-slate-300">Revenue Verifier Notes & Audit Reason:</label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add verification notes for immutable audit log..."
              className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>
      </div>

      {/* Rejection Modal */}
      {rejectionModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card max-w-md w-full rounded-2xl border border-rose-500/40 p-6 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2 text-rose-400">
              <XCircle className="w-5 h-5" />
              Confirm Document Rejection
            </h3>
            <p className="text-xs text-slate-300">
              Rejecting this document will mark it as fraudulent or unreadable in the audit logs and remove it from the digital cadastre.
            </p>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-200">Rejection Reason (Mandatory):</label>
              <textarea
                rows={3}
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="e.g. Severe water damage obscuring survey number beyond legal recovery..."
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setRejectionModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-xs font-bold text-white transition shadow-lg shadow-rose-950/40"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
