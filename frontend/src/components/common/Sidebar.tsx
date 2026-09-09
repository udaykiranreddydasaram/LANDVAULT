import React from 'react';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  FileText,
  CheckSquare,
  ScrollText,
  MapPin,
  BarChart3,
  History,
  Server,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  pendingCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, pendingCount }) => {
  const { user } = useAuth();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'documents', label: 'Documents Vault', icon: FileText },
    {
      id: 'verification',
      label: 'Verification Studio',
      icon: CheckSquare,
      badge: pendingCount > 0 ? pendingCount : undefined,
      badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    },
    { id: 'records', label: 'Digital Land Records', icon: ScrollText },
    { id: 'map', label: 'Cadastral GIS Map', icon: MapPin },
    { id: 'analytics', label: 'Analytics & KPIs', icon: BarChart3 },
    ...(user?.role === 'admin' ? [{ id: 'audit', label: 'Tamper Audit Trail', icon: History }] : []),
  ];

  return (
    <aside className="w-64 glass-panel border-r border-slate-800/80 flex flex-col justify-between p-4 shrink-0 min-h-[calc(100vh-61px)]">
      <div className="space-y-6">
        {/* Navigation Section */}
        <div>
          <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400 px-3 mb-2">
            Core Modules
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-emerald-600/90 to-emerald-700/70 text-white shadow-lg shadow-emerald-950/40 border border-emerald-500/30'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge !== undefined && (
                    <span
                      className={`text-[11px] px-2 py-0.5 rounded-full font-bold border ${item.badgeColor}`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* External Government Integration Status (Mocks) */}
        <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-2">
          <div className="flex items-center justify-between text-[11px] font-semibold text-slate-300">
            <span className="flex items-center gap-1.5">
              <Server className="w-3.5 h-3.5 text-emerald-400" />
              Govt Adapters
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">
              ACTIVE
            </span>
          </div>

          <div className="space-y-1.5 pt-1 text-[11px] text-slate-400 font-mono">
            <div className="flex items-center justify-between">
              <span>DILRMP Cadastre:</span>
              <span className="text-emerald-400 font-medium">Synced</span>
            </div>
            <div className="flex items-center justify-between">
              <span>State LRMS Portal:</span>
              <span className="text-emerald-400 font-medium">Live Mock</span>
            </div>
            <div className="flex items-center justify-between">
              <span>OCR Provider:</span>
              <span className="text-indigo-400 font-medium">Smart AI</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer info */}
      <div className="pt-4 border-t border-slate-800/80 text-[11px] text-slate-400 flex items-center justify-between">
        <span className="flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-emerald-400" />
          LANDVAULT AI v1.0
        </span>
        <span className="text-slate-400 font-mono">SIH 2026</span>
      </div>
    </aside>
  );
};
