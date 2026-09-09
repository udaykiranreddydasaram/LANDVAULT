import React, { useState } from 'react';
import {
  CheckSquare,
  AlertTriangle,
  Clock,
  ArrowRight,
  ShieldAlert,
  Search,
  CheckCircle2,
  XCircle,
  FileText,
} from 'lucide-react';
import { VerificationTask } from '../types';

interface VerificationQueuePageProps {
  tasks: VerificationTask[];
  onSelectTask: (taskId: number) => void;
  onRefresh: () => void;
}

export const VerificationQueuePage: React.FC<VerificationQueuePageProps> = ({
  tasks,
  onSelectTask,
  onRefresh,
}) => {
  const [filter, setFilter] = useState<string>('PENDING');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [search, setSearch] = useState<string>('');

  const filteredTasks = tasks.filter((t) => {
    if (filter !== 'ALL' && t.status !== filter) return false;
    if (priorityFilter !== 'ALL' && t.priority !== priorityFilter) return false;
    if (search) {
      const s = search.toLowerCase();
      return (
        (t.file_name && t.file_name.toLowerCase().includes(s)) ||
        (t.village && t.village.toLowerCase().includes(s)) ||
        (t.survey_number && t.survey_number.toLowerCase().includes(s))
      );
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
            <CheckSquare className="w-6 h-6 text-amber-400" />
            Human Verification Queue
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Human-in-the-Loop (HITL) audit queue for legacy documents with low OCR confidence, ink smudges, or rule exceptions.
          </p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 glass-card p-4 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-2">
          {/* Status filter */}
          <div className="flex items-center bg-slate-900/80 p-1 rounded-lg border border-slate-800 text-xs">
            {['PENDING', 'APPROVED', 'REJECTED', 'ALL'].map((st) => (
              <button
                key={st}
                onClick={() => setFilter(st)}
                className={`px-3 py-1.5 rounded-md font-semibold transition ${
                  filter === st
                    ? 'bg-amber-500 text-slate-950 shadow-sm shadow-amber-500/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {st === 'ALL' ? 'All Tasks' : st}
              </button>
            ))}
          </div>

          {/* Priority filter */}
          <div className="hidden sm:flex items-center bg-slate-900/80 p-1 rounded-lg border border-slate-800 text-xs">
            {['ALL', 'HIGH', 'MEDIUM'].map((pr) => (
              <button
                key={pr}
                onClick={() => setPriorityFilter(pr)}
                className={`px-2.5 py-1 rounded transition ${
                  priorityFilter === pr
                    ? 'bg-slate-700 text-white font-semibold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {pr === 'ALL' ? 'All Priority' : `${pr} Priority`}
              </button>
            ))}
          </div>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search village, survey no..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900/90 border border-slate-700 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
          />
        </div>
      </div>

      {/* Task Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredTasks.length === 0 ? (
          <div className="col-span-full text-center py-12 glass-card rounded-2xl border border-slate-800 text-slate-400">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2 opacity-80" />
            <div className="font-bold text-white text-base">All Caught Up!</div>
            <p className="text-xs text-slate-400 mt-1">No pending verification tasks matching current criteria.</p>
          </div>
        ) : (
          filteredTasks.map((task) => {
            const isHigh = task.priority === 'HIGH';
            return (
              <div
                key={task.id}
                className={`glass-card rounded-2xl p-5 border transition hover:border-amber-500/60 flex flex-col justify-between space-y-4 ${
                  isHigh ? 'border-amber-500/40 bg-gradient-to-b from-amber-950/20 to-slate-900/60' : 'border-slate-800'
                }`}
              >
                <div>
                  {/* Card Header: Priority & Status */}
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full uppercase tracking-wider border ${
                        isHigh
                          ? 'bg-rose-500/20 text-rose-300 border-rose-500/30 animate-pulse-subtle'
                          : 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                      }`}
                    >
                      {task.priority} Priority
                    </span>

                    <span
                      className={`text-[11px] font-bold px-2 py-0.5 rounded ${
                        task.status === 'APPROVED'
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : task.status === 'REJECTED'
                          ? 'bg-rose-500/20 text-rose-300'
                          : 'bg-amber-500/20 text-amber-300'
                      }`}
                    >
                      {task.status}
                    </span>
                  </div>

                  {/* Document Title */}
                  <div className="text-sm font-bold text-slate-100 flex items-center gap-2">
                    <FileText className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span className="truncate">{task.file_name}</span>
                  </div>

                  {/* Extracted snapshot */}
                  <div className="mt-3 p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1.5">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Village:</span>
                      <span className="font-semibold text-slate-200">{task.village || 'Pending OCR'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Survey No:</span>
                      <span className="font-mono font-bold text-amber-400">{task.survey_number || 'Unresolved'}</span>
                    </div>
                    <div className="flex justify-between items-center pt-1 border-t border-slate-800">
                      <span className="text-slate-400">AI Confidence:</span>
                      <span
                        className={`font-mono font-bold ${
                          (task.overall_confidence ?? 0) >= 0.70 ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {Math.round((task.overall_confidence ?? 0.6) * 100)}%
                      </span>
                    </div>
                  </div>

                  {/* Rejection reason or notes */}
                  {task.notes && (
                    <div className="mt-2 text-[11px] text-amber-300/80 bg-amber-950/30 p-2 rounded-lg border border-amber-500/20">
                      {task.notes}
                    </div>
                  )}
                </div>

                {/* Footer Action Button */}
                <button
                  onClick={() => onSelectTask(task.id)}
                  className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 text-xs font-bold transition flex items-center justify-center gap-2 shadow-lg shadow-amber-950/30"
                >
                  <span>Launch Verification Studio</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
