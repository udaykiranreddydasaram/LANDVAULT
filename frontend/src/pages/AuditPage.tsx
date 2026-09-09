import React, { useState, useEffect } from 'react';
import {
  History,
  Shield,
  Search,
  Filter,
  RefreshCw,
  User,
  Clock,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Lock,
} from 'lucide-react';
import { AuditLogItem } from '../types';
import { api } from '../services/api';

export const AuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionFilter, setActionFilter] = useState<string>('ALL');

  useEffect(() => {
    loadLogs();
  }, [actionFilter]);

  async function loadLogs() {
    try {
      setLoading(true);
      const data = await api.getAuditLogs(actionFilter !== 'ALL' ? actionFilter : undefined);
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit trail', err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
            <History className="w-6 h-6 text-indigo-400" />
            Tamper-Evident Audit Trail
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Immutable cryptographic compliance ledger recording every OCR extraction, field modification, and verification decision.
          </p>
        </div>

        <button
          onClick={loadLogs}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition border border-slate-700 self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Ledger
        </button>
      </div>

      {/* Security Guarantee Banner */}
      <div className="p-4 rounded-2xl bg-indigo-950/40 border border-indigo-500/40 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-indigo-200">
              Cryptographic Provenance Guarantee
            </div>
            <div className="text-xs text-indigo-300/80">
              Each modification stores the actor identity, IP address, previous value, and verified value in UTC timezone.
            </div>
          </div>
        </div>
        <span className="text-xs px-2.5 py-1 rounded bg-indigo-500/20 text-indigo-300 font-mono font-semibold border border-indigo-500/30">
          ADMIN CONFIDENTIAL
        </span>
      </div>

      {/* Filter Bar */}
      <div className="glass-card p-4 rounded-2xl border border-slate-800 flex items-center gap-2 text-xs">
        <span className="text-slate-400 font-medium px-2">Filter Action:</span>
        {['ALL', 'UPLOAD', 'EDIT_FIELD', 'APPROVE_RECORD', 'REJECT_RECORD', 'ROUTED_TO_VERIFICATION'].map(
          (act) => (
            <button
              key={act}
              onClick={() => setActionFilter(act)}
              className={`px-3 py-1.5 rounded-lg transition font-semibold ${
                actionFilter === act
                  ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-950/40'
                  : 'text-slate-400 hover:text-white bg-slate-900/60'
              }`}
            >
              {act === 'ALL' ? 'All Actions' : act.replace('_', ' ')}
            </button>
          )
        )}
      </div>

      {/* Audit Log Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-semibold">Timestamp (UTC)</th>
                <th className="pb-3 font-semibold">Operator / Actor</th>
                <th className="pb-3 font-semibold">Action</th>
                <th className="pb-3 font-semibold">Entity Target</th>
                <th className="pb-3 font-semibold">Audit Delta (Old vs New)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3.5 text-slate-400 whitespace-nowrap">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3.5">
                    <div className="font-sans font-bold text-slate-200">{log.performed_by}</div>
                    <div className="text-[10px] text-slate-400 font-mono uppercase">{log.performed_by_role}</div>
                  </td>
                  <td className="py-3.5">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        log.action.includes('APPROVE')
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : log.action.includes('REJECT')
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          : log.action.includes('EDIT')
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {log.action}
                    </span>
                  </td>
                  <td className="py-3.5 text-slate-300 font-sans">
                    <span className="text-[10px] text-slate-400 font-mono uppercase mr-1.5">
                      {log.entity_name}:
                    </span>
                    {log.entity_id}
                  </td>
                  <td className="py-3.5 text-[11px]">
                    {log.old_values || log.new_values ? (
                      <div className="p-2 rounded bg-slate-950 border border-slate-800 max-w-sm truncate text-slate-300">
                        {log.old_values && (
                          <div className="text-rose-400">
                            - {JSON.stringify(log.old_values)}
                          </div>
                        )}
                        {log.new_values && (
                          <div className="text-emerald-400">
                            + {JSON.stringify(log.new_values)}
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-slate-400 italic">No delta</span>
                    )}
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
