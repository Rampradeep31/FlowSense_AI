import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Map, RefreshCw } from 'lucide-react';

// Custom icons using Leaflet DivIcon for premium vector styling
const originIcon = L.divIcon({
  html: `<div style="width: 24px; height: 24px; border-radius: 50%; background-color: #10b981; border: 2px solid #ffffff; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); font-weight: bold; color: #ffffff; font-size: 11px;">A</div>`,
  className: 'custom-map-icon',
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

const destIcon = L.divIcon({
  html: `<div style="width: 24px; height: 24px; border-radius: 50%; background-color: #6366f1; border: 2px solid #ffffff; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); font-weight: bold; color: #ffffff; font-size: 11px;">B</div>`,
  className: 'custom-map-icon',
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

const createWeatherIcon = (temp) => L.divIcon({
  html: `<div style="padding: 2px 6px; border-radius: 6px; background-color: #0f172a; border: 1px solid #334155; font-size: 10px; font-weight: bold; color: #38bdf8; box-shadow: 0 2px 4px rgba(0,0,0,0.5); white-space: nowrap;">${Math.round(temp)}°C</div>`,
  className: 'custom-map-icon',
  iconSize: [45, 18],
  iconAnchor: [22, 9],
});

const createDisruptionIcon = (severity) => L.divIcon({
  html: `<div style="width: 20px; height: 20px; border-radius: 4px; background-color: ${severity === 'critical' ? '#ef4444' : '#f59e0b'}; border: 1px solid #ffffff; display: flex; align-items: center; justify-content: center; color: #ffffff; font-size: 10px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.4); animation: bounce 1.5s infinite;">⚠️</div>`,
  className: 'custom-map-icon animate-bounce',
  iconSize: [20, 20],
  iconAnchor: [10, 10],
});

export default function MapDashboard({ selectedShipment, riskCategory }) {
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedShipment) return;

    const fetchRouteStatus = async () => {
      try {
        setLoading(true);
        const resp = await fetch(`http://localhost:8000/api/v1/shipments/${selectedShipment.id}/status`);
        if (resp.ok) {
          const data = await resp.json();
          setRouteData(data);
        }
      } catch (err) {
        console.error('Failed to fetch route status details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRouteStatus();
  }, [selectedShipment]);

  // Center on Maharashtra (Mumbai-Pune region) by default
  const defaultCenter = [19.076, 72.8777];
  const center = routeData?.coordinates?.length > 0
    ? routeData.coordinates[Math.floor(routeData.coordinates.length / 2)]
    : defaultCenter;

  // Determine line color based on risk category
  const getPolylineColor = () => {
    if (selectedShipment?.status === 'spoiled' || riskCategory === 'high') return '#f43f5e'; // red
    if (selectedShipment?.status === 'delayed' || riskCategory === 'medium') return '#f59e0b'; // orange
    return '#10b981'; // green
  };

  return (
    <div className="glass-card rounded-2xl p-4 flex flex-col h-full border border-slate-800 bg-slate-900/60 backdrop-blur-md">
      <div className="flex justify-between items-center mb-3">
        <div>
          <h2 className="text-lg font-bold text-slate-100 font-outfit flex items-center gap-2">
            <Map className="h-5 w-5 text-emerald-400" />
            Route Telemetry & Weather Layer
          </h2>
          <p className="text-xs text-slate-400">Real-time corridor view from {selectedShipment?.origin || 'Mumbai'} to {selectedShipment?.destination || 'Pune'}</p>
        </div>
        {loading && <RefreshCw className="h-4 w-4 text-slate-400 animate-spin" />}
      </div>

      <div className="flex-1 rounded-xl overflow-hidden border border-slate-800 relative min-h-[300px] z-10">
        {routeData?.coordinates?.length > 0 ? (
          <MapContainer
            key={`${selectedShipment.id}-${routeData.coordinates.length}`}
            center={center}
            zoom={8.5}
            style={{ height: '100%', width: '100%', background: '#0b0f19' }}
          >
            {/* Dark Theme Map Tiles */}
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />

            {/* Polyline Route */}
            <Polyline
              positions={routeData.coordinates}
              pathOptions={{
                color: getPolylineColor(),
                weight: 4,
                opacity: 0.8,
                dashArray: selectedShipment?.status === 'delayed' ? '6, 6' : undefined
              }}
            />

            {/* Origin Marker */}
            <Marker position={routeData.coordinates[0]} icon={originIcon}>
              <Popup>
                <div className="text-xs font-semibold">Origin: {selectedShipment.origin}</div>
              </Popup>
            </Marker>

            {/* Destination Marker */}
            <Marker position={routeData.coordinates[routeData.coordinates.length - 1]} icon={destIcon}>
              <Popup>
                <div className="text-xs font-semibold">Destination: {selectedShipment.destination}</div>
              </Popup>
            </Marker>

            {/* Waypoint Weather Markers */}
            {routeData.weather_forecast && routeData.weather_forecast.map((wf, idx) => {
              // Ensure we have weather coordinates
              if (!wf.lat || !wf.lon) return null;
              return (
                <Marker
                  key={`weather-${idx}`}
                  position={[wf.lat, wf.lon]}
                  icon={createWeatherIcon(wf.temp)}
                >
                  <Popup>
                    <div className="p-1 text-slate-200">
                      <div className="font-bold text-xs">Weather Snapshot</div>
                      <div className="text-[11px] mt-1">Temp: {wf.temp}°C</div>
                      <div className="text-[11px]">Humidity: {wf.humidity}%</div>
                      <div className="text-[11px]">Precipitation: {Math.round((wf.pop || 0) * 100)}%</div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

            {/* News Disruptions Warning Markers */}
            {routeData.news_disruptions && routeData.news_disruptions.map((dis, idx) => {
              if (!dis.latitude || !dis.longitude) return null;
              return (
                <Marker
                  key={`news-${idx}`}
                  position={[dis.latitude, dis.longitude]}
                  icon={createDisruptionIcon(dis.severity)}
                >
                  <Popup>
                    <div className="p-1 text-slate-200">
                      <div className="font-bold text-xs text-rose-400 capitalize">{dis.severity} Incident</div>
                      <div className="text-[11px] mt-1">{dis.description}</div>
                      <div className="text-[10px] text-slate-400 mt-1">Source: {dis.source || 'Traffic Alert'}</div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}
          </MapContainer>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 text-sm gap-2 bg-slate-950/20">
            <div className="animate-pulse">Loading spatial routes...</div>
          </div>
        )}
      </div>
    </div>
  );
}
