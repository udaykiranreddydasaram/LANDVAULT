import React, { useState, useEffect } from 'react';
import {
  ScrollText,
  Search,
  CheckCircle,
  AlertTriangle,
  Award,
  ExternalLink,
  Printer,
  ShieldCheck,
  Server,
  Sparkles,
  MapPin,
  FileCheck,
} from 'lucide-react';
import { LandRecord } from '../types';
import { api } from '../services/api';

interface LandRecordsPageProps {
  onNavigateToMap: (surveyNo?: string) => void;
  initialRecordId?: number | null;
}

export const LandRecordsPage: React.FC<LandRecordsPageProps> = ({ onNavigateToMap, initialRecordId }) => {
  const [records, setRecords] = useState<LandRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [selectedRecord, setSelectedRecord] = useState<LandRecord | null>(null);
  const [certificateData, setCertificateData] = useState<any | null>(null);
  const [dilrmpStatus, setDilrmpStatus] = useState<any | null>(null);
  const [lrmsStatus, setLrmsStatus] = useState<any | null>(null);
  const [syncing, setSyncing] = useState<boolean>(false);

  useEffect(() => {
    async function loadRecords() {
      try {
        setLoading(true);
        const data = await api.listLandRecords();
        setRecords(data);
        if (initialRecordId) {
          const match = data.find((r) => r.id === initialRecordId);
          if (match) {
            openCertificate(match);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadRecords();
  }, [initialRecordId]);

  const openCertificate = async (rec: LandRecord) => {
    setSelectedRecord(rec);
    setDilrmpStatus(null);
    setLrmsStatus(null);
    try {
      const cert = await api.getLandRecordCertificate(rec.id);
      setCertificateData(cert);
    } catch (e) {
      console.error(e);
    }
  };

  const runGovernmentSync = async () => {
    if (!selectedRecord) return;
    setSyncing(true);
    try {
      const [dilrmpRes, lrmsRes] = await Promise.all([
        api.verifyDILRMP(selectedRecord.survey_number),
        api.syncLRMS(
          selectedRecord.record_identifier,
          selectedRecord.landowner_name,
          selectedRecord.survey_number,
          selectedRecord.land_area
        ),
      ]);
      setDilrmpStatus(dilrmpRes);
      setLrmsStatus(lrmsRes);
    } catch (e) {
      console.error(e);
    } finally {
      setSyncing(false);
    }
  };

  const filtered = records.filter((r) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (
      r.landowner_name.toLowerCase().includes(s) ||
      r.survey_number.toLowerCase().includes(s) ||
      r.record_identifier.toLowerCase().includes(s) ||
      r.village.toLowerCase().includes(s)
    );
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white flex items-center gap-2.5">
            <ScrollText className="w-6 h-6 text-emerald-400" />
            Digital Land Records Registry
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Authoritative digital repository of digitized, verified, and cadastral-aligned land parcels.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search landowner, survey no, khata..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl pl-10 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {/* Records Table */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-semibold">Record Identifier</th>
                <th className="pb-3 font-semibold">Landowner / Pattadar</th>
                <th className="pb-3 font-semibold">Location</th>
                <th className="pb-3 font-semibold">Survey No</th>
                <th className="pb-3 font-semibold">Extent</th>
                <th className="pb-3 font-semibold">Status</th>
                <th className="pb-3 font-semibold text-right">Certificate & GIS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((rec) => (
                <tr key={rec.id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3.5 font-mono font-bold text-emerald-400">
                    {rec.record_identifier}
                  </td>
                  <td className="py-3.5 font-medium text-slate-200">
                    <div>{rec.landowner_name}</div>
                    <div className="text-[10px] text-slate-400">{rec.ownership_type}</div>
                  </td>
                  <td className="py-3.5 text-slate-300">
                    <div>{rec.village}, {rec.mandal_tehsil}</div>
                    <div className="text-[10px] text-slate-400">{rec.district}, {rec.state}</div>
                  </td>
                  <td className="py-3.5 font-mono font-bold text-slate-100">
                    {rec.survey_number}
                  </td>
                  <td className="py-3.5 text-slate-200 font-medium">
                    {rec.land_area} {rec.area_unit}
                  </td>
                  <td className="py-3.5">
                    {rec.is_disputed ? (
                      <span className="px-2.5 py-1 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                        DISPUTED CLAIM
                      </span>
                    ) : rec.is_verified ? (
                      <span className="px-2.5 py-1 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1 w-fit">
                        <CheckCircle className="w-3 h-3" /> VERIFIED
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        IN REVIEW
                      </span>
                    )}
                  </td>
                  <td className="py-3.5 text-right space-x-2">
                    <button
                      onClick={() => onNavigateToMap(rec.survey_number)}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium transition inline-flex items-center gap-1"
                    >
                      <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                      GIS
                    </button>
                    <button
                      onClick={() => openCertificate(rec)}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600/90 hover:bg-emerald-500 text-white text-[11px] font-bold transition inline-flex items-center gap-1 shadow-sm shadow-emerald-950/30"
                    >
                      <FileCheck className="w-3.5 h-3.5" />
                      View Title
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Official Certificate Modal */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel max-w-2xl w-full rounded-2xl border border-emerald-500/40 p-6 space-y-5 max-h-[90vh] overflow-y-auto">
            {/* Certificate Header */}
            <div className="text-center border-b border-slate-800 pb-4 relative">
              <div className="w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center mx-auto mb-2">
                <Award className="w-6 h-6" />
              </div>
              <h2 className="text-lg font-black tracking-widest text-white uppercase">
                Digital Record of Rights (RoR)
              </h2>
              <p className="text-xs text-emerald-400 font-mono font-semibold">
                LANDVAULT AI VERIFIED TITLE DEED CERTIFICATE
              </p>
              <div className="text-[10px] text-slate-400 mt-0.5">
                Record Identifier: <span className="font-mono text-slate-200">{selectedRecord.record_identifier}</span>
              </div>
            </div>

            {/* Certificate Body Grid */}
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Pattadar / Owner</span>
                <div className="font-bold text-slate-100 text-sm">{selectedRecord.landowner_name}</div>
                <div className="text-slate-400">{selectedRecord.ownership_type}</div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Survey & Extent</span>
                <div className="font-mono font-bold text-amber-400 text-sm">
                  Survey No: {selectedRecord.survey_number}
                </div>
                <div className="text-slate-200">
                  {selectedRecord.land_area} {selectedRecord.area_unit} ({selectedRecord.land_classification})
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Cadastral Location</span>
                <div className="text-slate-200 font-medium">Village: {selectedRecord.village}</div>
                <div className="text-slate-400">
                  Mandal: {selectedRecord.mandal_tehsil} | District: {selectedRecord.district}
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Audit & Sealing</span>
                <div className="text-emerald-400 font-semibold flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" /> Digitally Sealed
                </div>
                <div className="text-slate-400 font-mono text-[10px]">
                  Verified: {selectedRecord.verified_at ? new Date(selectedRecord.verified_at).toLocaleDateString() : 'Auto-Promoted'}
                </div>
              </div>
            </div>

            {/* Government Sync Adapter Simulation */}
            <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <Server className="w-3.5 h-3.5 text-emerald-400" />
                  External Government API Interoperability (Mock Adapters)
                </span>
                <button
                  onClick={runGovernmentSync}
                  disabled={syncing}
                  className="px-2.5 py-1 rounded bg-slate-800 hover:bg-emerald-600 text-slate-200 hover:text-white text-[11px] font-semibold transition"
                >
                  {syncing ? 'Querying APIs...' : 'Simulate DILRMP & LRMS Push'}
                </button>
              </div>

              {dilrmpStatus && (
                <div className="p-2.5 rounded bg-slate-950 text-[11px] font-mono text-emerald-300 border border-emerald-500/20 space-y-1">
                  <div>[DILRMP Cadastre]: Status = {dilrmpStatus.dilrmp_sync_status} | ULPIN = {dilrmpStatus.ulpin}</div>
                  <div>[State LRMS Mutation]: Ref = {lrmsStatus?.state_portal_txn_ref} | Sign = {lrmsStatus?.state_revenue_officer_sign_status}</div>
                </div>
              )}
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-800">
              <button
                onClick={() => onNavigateToMap(selectedRecord.survey_number)}
                className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1"
              >
                <MapPin className="w-3.5 h-3.5" />
                View Cadastral Boundaries on GIS Map
              </button>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedRecord(null)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 transition"
                >
                  Close
                </button>
                <button
                  onClick={() => window.print()}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white transition flex items-center gap-1.5 shadow-md shadow-emerald-950/40"
                >
                  <Printer className="w-3.5 h-3.5" />
                  Print Official Extract
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
