import React from 'react';
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  Flame,
  ArrowUpRight,
  Upload,
  ExternalLink,
  ShieldCheck,
  Search,
} from 'lucide-react';
import { AnalyticsDashboardData, DocumentItem } from '../types';

interface DashboardPageProps {
  analytics: AnalyticsDashboardData | null;
  recentDocs: DocumentItem[];
  onNavigate: (tab: string, param?: any) => void;
  onOpenUpload: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  analytics,
  recentDocs,
  onNavigate,
  onOpenUpload,
}) => {
  const metrics = analytics?.metrics;

  const statCards = [
    {
      title: 'Total Ingested Records',
      value: metrics?.total_documents ?? 0,
      icon: FileText,
      color: 'from-blue-500/20 to-blue-600/10 text-blue-400 border-blue-500/30',
      tag: 'Scanned Deeds',
    },
    {
      title: 'Verified Digital Records',
      value: metrics?.verified_records ?? 0,
      icon: CheckCircle2,
      color: 'from-emerald-500/20 to-emerald-600/10 text-emerald-400 border-emerald-500/30',
      tag: 'Trusted Cadastre',
    },
    {
      title: 'Human Verification Queue',
      value: metrics?.pending_verification ?? 0,
      icon: AlertTriangle,
      color: 'from-amber-500/20 to-amber-600/10 text-amber-400 border-amber-500/30',
      tag: 'Requires Audit',
    },
    {
      title: 'Disputed / Duplicate Collisions',
      value: metrics?.disputed_records ?? 0,
      icon: Flame,
      color: 'from-rose-500/20 to-rose-600/10 text-rose-400 border-rose-500/30',
      tag: 'Fraud Blocked',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Welcome & Quick Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
            Cadastral Command Center
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30">
              Live Network
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Automated OCR ingestion, tri-factor confidence validation, and cadastral GIS mesh.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('map')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 text-sm font-semibold transition border border-slate-700"
          >
            <Search className="w-4 h-4 text-emerald-400" />
            Cadastral Map
          </button>
          <button
            onClick={onOpenUpload}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white text-sm font-semibold shadow-lg shadow-emerald-900/40 transition"
          >
            <Upload className="w-4 h-4" />
            Upload Legacy Deed
          </button>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className={`p-5 rounded-2xl bg-gradient-to-br ${card.color} border backdrop-blur-sm transition-all hover:scale-[1.01]`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 tracking-wide uppercase">
                  {card.title}
                </span>
                <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3 flex items-baseline justify-between">
                <div className="text-3xl font-extrabold text-white tracking-tight">{card.value}</div>
                <span className="text-[11px] px-2 py-0.5 rounded-md bg-slate-900/80 text-slate-300 font-mono">
                  {card.tag}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Verification Urgent Banner if any tasks pending */}
      {(metrics?.pending_verification ?? 0) > 0 && (
        <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-500/40 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400">
              <AlertTriangle className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="text-sm font-bold text-amber-200">
                Action Required: {metrics?.pending_verification} Records Awaiting Human Verification
              </div>
              <div className="text-xs text-amber-300/80">
                OCR confidence below 70% or validation rule exceptions detected on scanned physical deeds.
              </div>
            </div>
          </div>
          <button
            onClick={() => onNavigate('verification')}
            className="px-3.5 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold transition flex items-center gap-1.5"
          >
            Open Queue
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Grid: Recent Ingestions & Trust Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Ingested Documents (2 cols) */}
        <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-400" />
              Recent Ingested Documents
            </h2>
            <button
              onClick={() => onNavigate('documents')}
              className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1"
            >
              View All
              <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-3 font-semibold">Document Name</th>
                  <th className="pb-3 font-semibold">Type</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentDocs.slice(0, 5).map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-900/40 transition">
                    <td className="py-3 font-medium text-slate-200">
                      <div className="truncate max-w-[240px]">{doc.file_name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        Hash: {doc.file_hash.substring(0, 10)}...
                      </div>
                    </td>
                    <td className="py-3 text-slate-300">{doc.document_type}</td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          doc.status === 'VERIFIED'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : doc.status === 'REQUIRES_VERIFICATION'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {doc.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => {
                          if (doc.status === 'REQUIRES_VERIFICATION') {
                            onNavigate('verification');
                          } else {
                            onNavigate('records');
                          }
                        }}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium transition"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Cadastral AI Trust Overview (1 col) */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Automated Trust Index
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Multi-layer verification score computed across OCR token clarity, regex pattern fidelity, and cadastral deduplication.
            </p>

            <div className="mt-6 space-y-4">
              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-slate-300">Auto-Verification Rate</span>
                  <span className="text-emerald-400">{analytics?.metrics.auto_verification_rate ?? 75}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full"
                    style={{ width: `${analytics?.metrics.auto_verification_rate ?? 75}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold mb-1">
                  <span className="text-slate-300">Mean OCR Confidence</span>
                  <span className="text-indigo-400">
                    {Math.round((analytics?.metrics.average_confidence ?? 0.88) * 100)}%
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-blue-400 rounded-full"
                    style={{
                      width: `${Math.round((analytics?.metrics.average_confidence ?? 0.88) * 100)}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-400">
            <div className="font-semibold text-slate-200 mb-1">Hackathon Prototype Notice:</div>
            All data synthesized for SIH26018 demonstration. Integrated with mock DILRMP cadastral mesh and state mutation webhooks.
          </div>
        </div>
      </div>
    </div>
  );
};
