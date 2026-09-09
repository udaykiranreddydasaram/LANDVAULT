import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Shield, UserCheck, Eye, ShieldCheck, Database, RefreshCw } from 'lucide-react';
import { UserRole } from '../../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const { user, switchDemoRole } = useAuth();

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-3 flex items-center justify-between">
      {/* Brand Identity */}
      <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 via-teal-500 to-emerald-400 p-[2px] shadow-lg shadow-emerald-500/20">
          <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
            <Shield className="w-5 h-5 text-emerald-400" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-lg tracking-wider text-white">LANDVAULT</span>
            <span className="text-xs px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-bold border border-emerald-500/30">
              AI
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono border border-slate-700">
              SIH26018
            </span>
          </div>
          <p className="text-[11px] text-slate-400 hidden sm:block">From Legacy Records to Trusted Digital Land Data</p>
        </div>
      </div>

      {/* Center Hackathon Demo Banner */}
      <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span className="font-medium">Intelligent Cadastral Digitization Engine</span>
      </div>

      {/* Role Switcher & User Profile */}
      <div className="flex items-center gap-4">
        {/* Quick SIH Demo Role Switcher */}
        <div className="flex items-center bg-slate-900/90 border border-slate-800 rounded-lg p-1 text-xs">
          <span className="text-slate-400 px-2 font-medium hidden md:inline">Role:</span>
          <button
            onClick={() => switchDemoRole('verifier')}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-all ${
              user?.role === 'verifier'
                ? 'bg-emerald-600 text-white font-semibold shadow-sm shadow-emerald-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Revenue Inspector & Field Verifier"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Verifier</span>
          </button>
          <button
            onClick={() => switchDemoRole('admin')}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-all ${
              user?.role === 'admin'
                ? 'bg-indigo-600 text-white font-semibold shadow-sm shadow-indigo-500/30'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Director of Land Records (Full Access & Audit)"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Admin</span>
          </button>
          <button
            onClick={() => switchDemoRole('viewer')}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-all ${
              user?.role === 'viewer'
                ? 'bg-slate-700 text-white font-semibold'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Citizen / Bank Auditor (Read-Only)"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Viewer</span>
          </button>
        </div>

        {/* Current Active User Pill */}
        <div className="hidden sm:flex items-center gap-2 pl-2 border-l border-slate-800 text-right">
          <div>
            <div className="text-xs font-semibold text-slate-200">{user?.full_name || 'Revenue Officer'}</div>
            <div className="text-[10px] text-slate-400">{user?.department || 'Revenue Dept'}</div>
          </div>
        </div>
      </div>
    </header>
  );
};
