import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  FileText,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Eye,
  CheckSquare,
  ShieldCheck,
  Hash,
} from 'lucide-react';
import { DocumentDetail } from '../types';
import { api } from '../services/api';

interface DocumentDetailPageProps {
  documentId: number;
  onBack: () => void;
  onNavigateToVerification: () => void;
}

export const DocumentDetailPage: React.FC<DocumentDetailPageProps> = ({
  documentId,
  onBack,
  onNavigateToVerification,
}) => {
  const [detail, setDetail] = useState<DocumentDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [reprocessing, setReprocessing] = useState<boolean>(false);

  useEffect(() => {
    async function loadDoc() {
      try {
        setLoading(true);
        const data = await api.getDocumentDetail(documentId);
        setDetail(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadDoc();
  }, [documentId]);

  const handleReprocess = async () => {
    try {
      setReprocessing(true);
      const updated = await api.reprocessDocument(documentId);
      setDetail(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setReprocessing(false);
    }
  };

  if (loading || !detail) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-xs text-slate-400">Loading Document Inspection Data...</div>
      </div>
    );
  }

  let imageSrc = `http://localhost:8000/samples/Sample_Patta_Deed_Telangana_Clean.png`;
  if (detail.file_name.includes('Smudged') || detail.file_name.includes('1988')) {
    imageSrc = `http://localhost:8000/samples/Sample_Patta_Deed_Telangana_Smudged_1988.png`;
  } else if (detail.file_name.includes('Maharashtra') || detail.file_name.includes('7_12')) {
    imageSrc = `http://localhost:8000/samples/Sample_7_12_Extract_Maharashtra.png`;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-4 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-white truncate max-w-md">{detail.file_name}</h1>
              <span
                className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                  detail.status === 'VERIFIED'
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : detail.status === 'REQUIRES_VERIFICATION'
                    ? 'bg-amber-500/20 text-amber-300'
                    : 'bg-slate-800 text-slate-300'
                }`}
              >
                {detail.status.replace('_', ' ')}
              </span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono mt-0.5">
              SHA-256: {detail.file_hash}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {detail.status === 'REQUIRES_VERIFICATION' && (
            <button
              onClick={onNavigateToVerification}
              className="px-3.5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold transition flex items-center gap-1.5 shadow-md shadow-amber-950/40"
            >
              <CheckSquare className="w-4 h-4" />
              Open Verification Studio
            </button>
          )}
          <button
            onClick={handleReprocess}
            disabled={reprocessing}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition border border-slate-700 flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reprocessing ? 'animate-spin' : ''}`} />
            Re-run OCR & Rules
          </button>
        </div>
      </div>

      {/* Grid: Document Scanned Image vs Extracted Fields */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Scanned Document Image (5 cols) */}
        <div className="lg:col-span-5 glass-card rounded-2xl p-5 border border-slate-800 space-y-3 flex flex-col">
          <div className="text-xs font-bold text-slate-300 uppercase tracking-wide">
            Source Physical Document
          </div>
          <div className="flex-1 bg-slate-950 rounded-xl p-3 border border-slate-800 flex items-center justify-center overflow-auto">
            <img src={imageSrc} alt="Scanned Deed" className="max-w-full rounded border border-slate-700" />
          </div>
          <div className="text-[11px] text-slate-400 font-mono flex justify-between">
            <span>Provider: {detail.ocr_provider}</span>
            <span>Size: {Math.round(detail.file_size_bytes / 1024)} KB</span>
          </div>
        </div>

        {/* Right: Extracted Fields & Validation Rules (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Extracted Fields Table */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Extracted Cadastral Attributes ({detail.fields.length} Fields)
            </h2>

            <div className="divide-y divide-slate-800/60 text-xs">
              {detail.fields.map((f) => (
                <div key={f.field} className="py-2.5 flex items-center justify-between gap-4">
                  <div className="w-1/3">
                    <span className="font-semibold text-slate-300 capitalize">
                      {f.field.replace('_', ' ')}:
                    </span>
                  </div>
                  <div className="flex-1 font-mono text-slate-200 truncate">
                    {f.value || <span className="text-slate-400 italic">Not detected</span>}
                  </div>
                  <div className="w-28 text-right">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono ${
                        f.confidence >= 0.9
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : f.confidence >= 0.7
                          ? 'bg-amber-500/20 text-amber-300'
                          : 'bg-rose-500/20 text-rose-300'
                      }`}
                    >
                      {Math.round(f.confidence * 100)}% Conf
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Validation Results */}
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Automated Validation Rule Audit
            </h2>

            <div className="space-y-2">
              {detail.validation_results.map((vr, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-xl border text-xs flex items-center justify-between ${
                    vr.status === 'PASSED'
                      ? 'bg-emerald-950/20 border-emerald-500/20 text-emerald-300'
                      : 'bg-rose-950/30 border-rose-500/30 text-rose-300'
                  }`}
                >
                  <div>
                    <span className="font-mono font-bold mr-2">[{vr.rule_code}]</span>
                    <span>{vr.message}</span>
                  </div>
                  <span className="font-bold font-mono text-[10px] uppercase">{vr.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
