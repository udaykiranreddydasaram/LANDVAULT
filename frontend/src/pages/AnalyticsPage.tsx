import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  Cell,
} from 'recharts';
import {
  BarChart3,
  TrendingUp,
  ShieldCheck,
  AlertTriangle,
  MapPin,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';
import { AnalyticsDashboardData } from '../types';
import { api } from '../services/api';

interface AnalyticsPageProps {
  analytics: AnalyticsDashboardData | null;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({ analytics: initialAnalytics }) => {
  const [data, setData] = useState<AnalyticsDashboardData | null>(initialAnalytics);
  const [loading, setLoading] = useState<boolean>(!initialAnalytics);

  const fetchFreshData = async () => {
    try {
      setLoading(true);
      const res = await api.getAnalyticsDashboard();
      setData(res);
    } catch (err) {
      console.error('Failed to load analytics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFreshData();
  }, []);

  if (!data && loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-xs text-slate-400 flex items-center gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-emerald-400" />
          <span>Loading Analytics & Performance Metrics...</span>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <button
          onClick={fetchFreshData}
          className="px-4 py-2 rounded-xl bg-slate-800 text-xs text-slate-300 hover:text-white"
        >
          Failed to load metrics. Click to retry.
        </button>
      </div>
    );
  }

  const { metrics, confidence_distribution, top_rule_failures, village_stats, recent_ingestion_trend } = data;

  const confidenceData = [
    { name: 'High (90-100%)', count: confidence_distribution.high_count, fill: '#10b981' },
    { name: 'Medium (70-89%)', count: confidence_distribution.medium_count, fill: '#f59e0b' },
    { name: 'Low (0-69%)', count: confidence_distribution.low_count, fill: '#ef4444' },
  ];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
            <BarChart3 className="w-6 h-6 text-emerald-400" />
            Analytics & System Intelligence
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time metrics on ingestion velocity, OCR confidence distribution, and cadastral validation performance.
          </p>
        </div>
        <button
          onClick={fetchFreshData}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition border border-slate-700 self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-400' : ''}`} />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 uppercase font-semibold">Digitization Rate</span>
          <div className="text-2xl font-black text-white">{metrics.auto_verification_rate}%</div>
          <div className="text-[10px] text-emerald-400 font-medium">Automatic pass without human edits</div>
        </div>
        <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 uppercase font-semibold">Mean OCR Confidence</span>
          <div className="text-2xl font-black text-indigo-400">
            {Math.round(metrics.average_confidence * 100)}%
          </div>
          <div className="text-[10px] text-slate-400 font-mono">Weighted tri-factor metric</div>
        </div>
        <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 uppercase font-semibold">Verified Cadastre</span>
          <div className="text-2xl font-black text-emerald-400">{metrics.verified_records}</div>
          <div className="text-[10px] text-slate-400 font-mono">Official digital titles</div>
        </div>
        <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-[11px] text-slate-400 uppercase font-semibold">Fraud / Collisions</span>
          <div className="text-2xl font-black text-rose-400">{metrics.disputed_records}</div>
          <div className="text-[10px] text-rose-400 font-medium">Cadastral overlap blocked</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ingestion & Verification Velocity (Area Chart) */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              Weekly Ingestion & Digitization Velocity
            </h2>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
              Last 7 Days
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={recent_ingestion_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorIngested" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorVerified" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="ingested" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorIngested)" />
                <Area type="monotone" dataKey="verified" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorVerified)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center justify-center gap-6 text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
              <span>Documents Ingested</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <span>Promoted to Cadastre</span>
            </div>
          </div>
        </div>

        {/* OCR Confidence Distribution (Bar Chart) */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              OCR Field-Level Confidence Spectrum
            </h2>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
              All Fields
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={confidenceData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                />
                <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                  {confidenceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="text-[11px] text-slate-400 text-center">
            Fields below 70% automatically trigger Human-in-the-Loop audit routing.
          </div>
        </div>
      </div>

      {/* Bottom Row: Village Completion & Top Exceptions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Village Progress */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <MapPin className="w-4 h-4 text-emerald-400" />
            Cadastral Digitization Progress by Village
          </h2>

          <div className="space-y-3 pt-2">
            {village_stats.map((vs, i) => (
              <div key={i} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <div>
                    <span className="font-bold text-slate-200">{vs.village}</span>
                    <span className="text-[10px] text-slate-400 ml-1.5">({vs.district})</span>
                  </div>
                  <span className="font-mono font-bold text-emerald-400">{vs.completion_percentage}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full"
                    style={{ width: `${vs.completion_percentage}%` }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                  <span>{vs.verified_count} Verified</span>
                  <span>{vs.total_records} Total Deeds</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Validation Rule Exceptions */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Top Triggered Validation Exceptions
          </h2>

          <div className="space-y-3 pt-2">
            {top_rule_failures.map((rf, i) => (
              <div key={i} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="font-mono text-xs font-bold text-amber-300">[{rf.rule_code}]</div>
                  <div className="text-xs text-slate-300 mt-0.5">{rf.rule_name}</div>
                </div>
                <div className="text-right">
                  <span className="px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold font-mono text-xs">
                    {rf.failure_count} triggers
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
