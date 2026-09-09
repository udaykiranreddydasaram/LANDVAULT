import React, { useState, useRef } from 'react';
import {
  Upload,
  FileText,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Eye,
  FileSearch,
  Sparkles,
  ShieldAlert,
} from 'lucide-react';
import { DocumentItem, DocumentDetail } from '../types';
import { api } from '../services/api';

interface DocumentsPageProps {
  documents: DocumentItem[];
  onRefresh: () => void;
  onSelectDocument: (doc: DocumentItem) => void;
  onNavigateToVerification: () => void;
}

export const DocumentsPage: React.FC<DocumentsPageProps> = ({
  documents,
  onRefresh,
  onSelectDocument,
  onNavigateToVerification,
}) => {
  const [filter, setFilter] = useState<string>('ALL');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [lastUploadedDoc, setLastUploadedDoc] = useState<DocumentItem | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const filteredDocs = documents.filter((doc) => {
    if (filter === 'ALL') return true;
    return doc.status === filter;
  });

  const handleFileUpload = async (file: File, allowDuplicate: boolean = false) => {
    setIsUploading(true);
    setUploadError(null);
    setSuccessMsg(null);
    try {
      const doc = await api.uploadDocument(file, 'Pattadar Passbook / ROR', allowDuplicate);
      setLastUploadedDoc(doc);
      setSuccessMsg(`Document "${doc.file_name}" uploaded and processed successfully! Status: ${doc.status}`);
      onRefresh();
    } catch (err: any) {
      setUploadError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  // One-Click Demo Sample Uploaders
  const uploadDemoSample = async (sampleType: 'smudge' | 'clean' | 'pune') => {
    setIsUploading(true);
    setUploadError(null);
    setSuccessMsg(null);

    let filename = 'Sample_Patta_Deed_Telangana_Smudged_1988.png';
    let docType = 'Pattadar Passbook / ROR';
    if (sampleType === 'clean') {
      filename = 'Sample_Patta_Deed_Telangana_Clean.png';
    } else if (sampleType === 'pune') {
      filename = 'Sample_7_12_Extract_Maharashtra.png';
      docType = '7/12 Extract';
    }

    try {
      // Fetch sample file from backend static mount
      const res = await fetch(`http://localhost:8000/samples/${filename}`);
      const blob = await res.blob();
      const file = new File([blob], filename, { type: 'image/png' });
      await handleFileUpload(file, true);
    } catch (err: any) {
      setUploadError(`Failed loading sample deed: ${err.message}`);
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
            <FileText className="w-6 h-6 text-emerald-400" />
            Documents Vault & Ingestion
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Upload legacy scanned land deeds for automated computer vision preprocessing and OCR extraction.
          </p>
        </div>
        <button
          onClick={onRefresh}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition border border-slate-700 self-start"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh Registry
        </button>
      </div>

      {/* Upload Zone & Demo Presets */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Drag-and-Drop Area */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wide">
            Upload Land Record Document
          </h2>

          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-700 hover:border-emerald-500/60 bg-slate-900/40 hover:bg-slate-900/70 rounded-xl p-8 text-center cursor-pointer transition flex flex-col items-center justify-center gap-3"
          >
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              accept=".pdf,.png,.jpg,.jpeg,.tiff"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />
            <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
              <Upload className="w-6 h-6" />
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-200">
                Click to browse or drag & drop scanned deed
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Supports PDF, TIFF, JPG, PNG (Legacy stamp papers, Patta Passbooks, 7/12 Extracts)
              </div>
            </div>
          </div>

          {/* Feedback messages */}
          {isUploading && (
            <div className="flex items-center gap-2 text-xs text-emerald-400 p-3 rounded-lg bg-emerald-950/40 border border-emerald-500/30">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Processing document: Running OCR, spatial extraction & rule engine...</span>
            </div>
          )}
          {uploadError && (
            <div className="flex items-center gap-2 text-xs text-rose-400 p-3 rounded-lg bg-rose-950/40 border border-rose-500/30">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
          {successMsg && (
            <div className="space-y-2 p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-xs">
              <div className="flex items-center gap-2 text-emerald-300 font-semibold">
                <CheckCircle className="w-4 h-4 shrink-0 text-emerald-400" />
                <span>{successMsg}</span>
              </div>
              {lastUploadedDoc && (
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  <button
                    onClick={() => onSelectDocument(lastUploadedDoc)}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm shadow-emerald-950"
                  >
                    <FileSearch className="w-3.5 h-3.5" />
                    <span>Inspect OCR Extraction & Rules</span>
                  </button>
                  {lastUploadedDoc.status === 'REQUIRES_VERIFICATION' && (
                    <button
                      onClick={onNavigateToVerification}
                      className="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition flex items-center gap-1.5"
                    >
                      <span>Open Verification Studio</span>
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Hackathon Demo Presets (One-Click Testing) */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-wide">
              <Sparkles className="w-4 h-4" />
              SIH Judging Quick-Presets
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Select a pre-calibrated historical deed to demonstrate end-to-end pipeline features in seconds:
            </p>

            <div className="mt-4 space-y-2.5">
              <button
                disabled={isUploading}
                onClick={() => uploadDemoSample('smudge')}
                className="w-full text-left p-3 rounded-xl bg-amber-950/30 hover:bg-amber-900/40 border border-amber-500/40 transition group"
              >
                <div className="flex items-center justify-between text-xs font-bold text-amber-300">
                  <span>1. Smudged Patta Deed (1988)</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    Low Conf
                  </span>
                </div>
                <div className="text-[11px] text-amber-200/70 mt-1">
                  Smudge on Survey No triggers human verification queue.
                </div>
              </button>

              <button
                disabled={isUploading}
                onClick={() => uploadDemoSample('clean')}
                className="w-full text-left p-3 rounded-xl bg-emerald-950/30 hover:bg-emerald-900/40 border border-emerald-500/40 transition group"
              >
                <div className="flex items-center justify-between text-xs font-bold text-emerald-300">
                  <span>2. Clean Passbook Extract</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    Auto-Verified
                  </span>
                </div>
                <div className="text-[11px] text-emerald-200/70 mt-1">
                  High confidence (97%), instant GIS parcel promotion.
                </div>
              </button>

              <button
                disabled={isUploading}
                onClick={() => uploadDemoSample('pune')}
                className="w-full text-left p-3 rounded-xl bg-indigo-950/30 hover:bg-indigo-900/40 border border-indigo-500/40 transition group"
              >
                <div className="flex items-center justify-between text-xs font-bold text-indigo-300">
                  <span>3. Maharashtra Form VII-XII</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    Multi-State
                  </span>
                </div>
                <div className="text-[11px] text-indigo-200/70 mt-1">
                  Wagholi, Pune cadastral extraction.
                </div>
              </button>
            </div>
          </div>

          <div className="text-[11px] text-slate-400 italic">
            * Uses smart OCR simulator for zero demo failure risk.
          </div>
        </div>
      </div>

      {/* Documents Registry Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <FileSearch className="w-4 h-4 text-emerald-400" />
            Ingested Document Library ({filteredDocs.length})
          </h2>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 bg-slate-900/80 p-1 rounded-lg border border-slate-800 text-xs">
            {['ALL', 'VERIFIED', 'REQUIRES_VERIFICATION', 'REJECTED'].map((st) => (
              <button
                key={st}
                onClick={() => setFilter(st)}
                className={`px-2.5 py-1 rounded transition ${
                  filter === st
                    ? 'bg-emerald-600 text-white font-semibold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {st === 'ALL' ? 'All Records' : st.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-semibold">ID</th>
                <th className="pb-3 font-semibold">Document Name</th>
                <th className="pb-3 font-semibold">Type</th>
                <th className="pb-3 font-semibold">File Hash (SHA-256)</th>
                <th className="pb-3 font-semibold">Status</th>
                <th className="pb-3 font-semibold">Uploaded</th>
                <th className="pb-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredDocs.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3.5 font-mono text-slate-400">#{doc.id}</td>
                  <td className="py-3.5 font-medium text-slate-200">
                    <div className="truncate max-w-[220px]">{doc.file_name}</div>
                    <div className="text-[10px] text-slate-400">{Math.round(doc.file_size_bytes / 1024)} KB</div>
                  </td>
                  <td className="py-3.5 text-slate-300">{doc.document_type}</td>
                  <td className="py-3.5 font-mono text-slate-400 text-[11px]">
                    {doc.file_hash.substring(0, 16)}...
                  </td>
                  <td className="py-3.5">
                    <span
                      className={`px-2.5 py-1 rounded text-[10px] font-bold tracking-wider ${
                        doc.status === 'VERIFIED'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : doc.status === 'REQUIRES_VERIFICATION'
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          : doc.status === 'REJECTED'
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {doc.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3.5 text-slate-400">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-3.5 text-right">
                    <button
                      onClick={() => onSelectDocument(doc)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition border border-slate-700"
                    >
                      <Eye className="w-3.5 h-3.5 text-emerald-400" />
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
