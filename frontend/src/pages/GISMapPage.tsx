import React, { useState, useEffect, useRef } from 'react';
import {
  MapPin,
  Layers,
  Search,
  Filter,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  Info,
  Maximize2,
  X,
} from 'lucide-react';
import L from 'leaflet';
import { GeoJSONFeatureCollection, GeoJSONFeature } from '../types';
import { api } from '../services/api';

interface GISMapPageProps {
  initialSurveyNo?: string;
  onNavigateToRecord?: (recordId: number) => void;
}

export const GISMapPage: React.FC<GISMapPageProps> = ({ initialSurveyNo, onNavigateToRecord }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const geojsonLayerRef = useRef<L.GeoJSON | null>(null);

  const [parcelsData, setParcelsData] = useState<GeoJSONFeatureCollection | null>(null);
  const [selectedParcel, setSelectedParcel] = useState<GeoJSONFeature | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>(initialSurveyNo || '');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [villageFilter, setVillageFilter] = useState<string>('ALL');
  const [mapType, setMapType] = useState<'osm' | 'satellite'>('osm');

  // Load GIS Parcels GeoJSON
  useEffect(() => {
    async function fetchParcels() {
      try {
        const data = await api.getGISParcels(
          villageFilter !== 'ALL' ? villageFilter : undefined,
          statusFilter !== 'ALL' ? statusFilter : undefined
        );
        setParcelsData(data);
      } catch (err) {
        console.error('Failed to load cadastral parcels', err);
      }
    }
    fetchParcels();
  }, [villageFilter, statusFilter]);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Default center: Shamshabad, Telangana
    const map = L.map(mapContainerRef.current, {
      center: [17.2530, 78.4410],
      zoom: 15,
      zoomControl: false,
    });

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Tile layers
    const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    });

    osmLayer.addTo(map);
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update GeoJSON layer when parcelsData changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !parcelsData) return;

    // Remove old layer
    if (geojsonLayerRef.current) {
      map.removeLayer(geojsonLayerRef.current);
    }

    const geoLayer = L.geoJSON(parcelsData as any, {
      style: (feature: any) => {
        const status = feature.properties?.status;
        let color = '#10b981'; // Verified: Emerald
        let fillOpacity = 0.45;

        if (status === 'DISPUTED') {
          color = '#ef4444'; // Red
          fillOpacity = 0.65;
        } else if (status === 'PENDING_REVIEW') {
          color = '#f59e0b'; // Amber
          fillOpacity = 0.50;
        }

        return {
          color: color,
          weight: 2.5,
          opacity: 0.9,
          fillColor: color,
          fillOpacity: fillOpacity,
        };
      },
      onEachFeature: (feature: any, layer: L.Layer) => {
        const p = feature.properties;
        layer.on({
          click: () => {
            setSelectedParcel(feature as GeoJSONFeature);
          },
          mouseover: (e: any) => {
            const l = e.target;
            l.setStyle({ weight: 4, fillOpacity: 0.8 });
          },
          mouseout: (e: any) => {
            geoLayer.resetStyle(e.target);
          },
        });

        // Tooltip
        layer.bindTooltip(
          `<strong>Survey ${p.survey_number}</strong><br/>${p.landowner_name || 'Record'}<br/>${p.land_area || ''} ${p.area_unit || ''}`,
          { direction: 'top', sticky: true, className: 'leaflet-custom-tooltip' }
        );
      },
    }).addTo(map);

    geojsonLayerRef.current = geoLayer;

    // If there are parcels, fit bounds
    if (parcelsData.features.length > 0) {
      map.fitBounds(geoLayer.getBounds(), { padding: [40, 40], maxZoom: 16 });
    }
  }, [parcelsData]);

  // Jump to specific survey number search
  const handleSearchSurvey = () => {
    if (!searchQuery || !parcelsData || !mapInstanceRef.current) return;
    const match = parcelsData.features.find((f) =>
      f.properties.survey_number.toLowerCase().includes(searchQuery.toLowerCase().trim())
    );
    if (match) {
      setSelectedParcel(match);
      const coords = match.geometry.coordinates[0];
      const lat = coords[0][1];
      const lng = coords[0][0];
      mapInstanceRef.current.flyTo([lat, lng], 17, { duration: 1.2 });
    } else {
      alert(`Survey Number "${searchQuery}" not found in current GIS mesh.`);
    }
  };

  return (
    <div className="space-y-4">
      {/* Map Control Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 glass-card p-4 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-extrabold text-white flex items-center gap-2">
              Cadastral GIS Map Engine
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono">
                OpenStreetMap
              </span>
            </h1>
            <p className="text-[11px] text-slate-400">
              Interactive cadastral boundaries synchronized with verified digital land deeds.
            </p>
          </div>
        </div>

        {/* Search & Village Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Survey No Search */}
          <div className="flex items-center gap-1 bg-slate-900 border border-slate-700 rounded-xl px-2.5 py-1 text-xs">
            <input
              type="text"
              placeholder="Jump to Survey No (e.g. 148/2)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearchSurvey()}
              className="bg-transparent border-none text-slate-200 placeholder-slate-500 focus:outline-none w-48 font-mono text-xs"
            />
            <button
              onClick={handleSearchSurvey}
              className="p-1 rounded bg-slate-800 hover:bg-emerald-600 text-slate-300 hover:text-white transition"
            >
              <Search className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Village Filter */}
          <select
            value={villageFilter}
            onChange={(e) => setVillageFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="ALL">All Villages</option>
            <option value="Mamidipally">Mamidipally (Telangana)</option>
            <option value="Wagholi">Wagholi (Maharashtra)</option>
            <option value="Bakas">Bakas (Uttar Pradesh)</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
          >
            <option value="ALL">All Cadastral Status</option>
            <option value="VERIFIED">Verified (Green)</option>
            <option value="DISPUTED">Disputed / Conflict (Red)</option>
            <option value="PENDING_REVIEW">Pending Audit (Amber)</option>
          </select>
        </div>
      </div>

      {/* Map Container Viewport */}
      <div className="relative glass-card rounded-2xl border border-slate-800 h-[650px] overflow-hidden">
        <div ref={mapContainerRef} className="w-full h-full z-0" />

        {/* Cadastral Legend Float */}
        <div className="absolute top-4 left-4 z-10 glass-panel p-3 rounded-xl border border-slate-700/80 text-xs space-y-2 shadow-xl">
          <div className="font-bold text-slate-200 text-[11px] tracking-wide uppercase">Cadastral Legend</div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-emerald-500/80 border border-emerald-400"></span>
            <span className="text-slate-300 text-[11px]">Verified Digital Parcel</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-amber-500/80 border border-amber-400"></span>
            <span className="text-slate-300 text-[11px]">Pending Verification</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded bg-rose-500/80 border border-rose-400 animate-pulse"></span>
            <span className="text-slate-300 text-[11px]">Disputed Duplicate Collision</span>
          </div>
        </div>

        {/* Selected Parcel Slide-Over Drawer */}
        {selectedParcel && (
          <div className="absolute top-4 right-4 z-10 glass-panel max-w-sm w-full rounded-2xl border border-emerald-500/40 p-5 space-y-4 shadow-2xl animate-fade-in">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-300 uppercase">Cadastral Parcel</span>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                    selectedParcel.properties.status === 'VERIFIED'
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : 'bg-rose-500/20 text-rose-300'
                  }`}
                >
                  {selectedParcel.properties.status}
                </span>
              </div>
              <button
                onClick={() => setSelectedParcel(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Survey Number</span>
                <div className="text-lg font-extrabold font-mono text-amber-400">
                  {selectedParcel.properties.survey_number}
                </div>
              </div>

              <div>
                <span className="text-[10px] text-slate-400 uppercase font-semibold">Pattadar / Owner</span>
                <div className="text-sm font-bold text-slate-100">
                  {selectedParcel.properties.landowner_name || 'Government Cadastre'}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400">Land Extent</span>
                  <div className="font-semibold text-slate-200">
                    {selectedParcel.properties.land_area} {selectedParcel.properties.area_unit}
                  </div>
                </div>
                <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400">Khata No</span>
                  <div className="font-semibold text-slate-200">
                    {selectedParcel.properties.khata_number || 'N/A'}
                  </div>
                </div>
              </div>

              <div className="text-[11px] text-slate-400">
                Location: {selectedParcel.properties.village}, {selectedParcel.properties.district},{' '}
                {selectedParcel.properties.state}
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <button
                onClick={() => {
                  if (onNavigateToRecord) {
                    onNavigateToRecord(selectedParcel.properties.land_record_id);
                  }
                }}
                className="w-full py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-md shadow-emerald-950/40"
              >
                <span>View Full Digital Title Certificate</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
