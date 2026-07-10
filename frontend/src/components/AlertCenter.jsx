import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Bell, X } from 'lucide-react';

export default function AlertCenter({ onAlertUpdate }) {
  const [alerts, setAlerts] = useState([]);
  const [showCenter, setShowCenter] = useState(false);

  useEffect(() => {
    let socket;
    let timeoutId;
    
    const connect = () => {
      const wsUrl = `ws://${window.location.hostname}:8000/api/v1/alerts/ws`;
      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        console.log('Alert WebSocket connected');
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Received WebSocket alert event:', data);
          setAlerts((prev) => [data, ...prev]);
          if (onAlertUpdate) {
            onAlertUpdate(data);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket alert payload:', err);
        }
      };

      socket.onerror = (error) => {
        console.error('Alert WebSocket error:', error);
      };

      socket.onclose = () => {
        console.log('Alert WebSocket disconnected. Reconnecting in 5s...');
        timeoutId = setTimeout(connect, 5000);
      };
    };

    connect();

    return () => {
      if (socket) socket.close();
      clearTimeout(timeoutId);
    };
  }, [onAlertUpdate]);

  const handleAcknowledge = async (alertId) => {
    try {
      const resp = await fetch(`http://localhost:8000/api/v1/alerts/${alertId}/acknowledge`, {
        method: 'POST',
      });
      if (resp.ok) {
        // Update local status
        setAlerts((prev) =>
          prev.map((alt) =>
            alt.id === alertId ? { ...alt, acknowledged: true } : alt
          )
        );
        if (onAlertUpdate) {
          onAlertUpdate();
        }
      }
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const activeAlerts = alerts.filter((alt) => !alt.acknowledged);

  return (
    <div className="relative">
      {/* Alert Bell Button */}
      <button
        onClick={() => setShowCenter(!showCenter)}
        className="relative p-2 rounded-full bg-slate-800 border border-slate-700 hover:bg-slate-700 transition duration-200"
      >
        <Bell className="h-5 w-5 text-slate-300" />
        {activeAlerts.length > 0 && (
          <span className="absolute top-0 right-0 h-4 w-4 bg-rose-500 rounded-full flex items-center justify-center text-[10px] font-bold text-white animate-pulse">
            {activeAlerts.length}
          </span>
        )}
      </button>

      {/* Floating Alert Center Panel */}
      {showCenter && (
        <div className="absolute right-0 mt-3 w-80 max-h-[400px] overflow-y-auto rounded-xl border border-slate-700 bg-slate-900 bg-opacity-95 backdrop-blur-md shadow-2xl p-4 z-50 animate-slide-in">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
            <h3 className="font-semibold text-slate-100 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              Active System Alerts
            </h3>
            <button
              onClick={() => setShowCenter(false)}
              className="text-slate-400 hover:text-slate-200"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {alerts.length === 0 ? (
            <div className="text-center py-6 text-sm text-slate-500">
              No recent cold chain alerts detected.
            </div>
          ) : (
            <div className="space-y-3">
              {alerts.map((alt) => (
                <div
                  key={alt.id}
                  className={`p-3 rounded-lg border text-sm transition-all duration-300 ${
                    alt.acknowledged
                      ? 'bg-slate-950 border-slate-800 bg-opacity-40 opacity-60'
                      : alt.severity === 'critical'
                      ? 'bg-rose-950 bg-opacity-30 border-rose-800 border-opacity-60 shadow-[0_0_10px_rgba(244,63,94,0.15)]'
                      : 'bg-amber-950 bg-opacity-30 border-amber-800 border-opacity-60'
                  }`}
                >
                  <div className="flex justify-between items-start gap-2">
                    <span
                      className={`font-semibold capitalize text-xs px-1.5 py-0.5 rounded ${
                        alt.severity === 'critical'
                          ? 'bg-rose-500 bg-opacity-20 text-rose-400'
                          : 'bg-amber-500 bg-opacity-20 text-amber-400'
                      }`}
                    >
                      {alt.severity}
                    </span>
                    <span className="text-[10px] text-slate-500">
                      Shipment #{alt.shipment_id}
                    </span>
                  </div>
                  
                  <p className="mt-1 text-slate-300 leading-snug">{alt.message}</p>
                  
                  {alt.why_info && (
                    <div className="mt-2 text-[11px] text-slate-400 bg-slate-950 bg-opacity-50 p-1.5 rounded font-mono">
                      {JSON.stringify(alt.why_info)}
                    </div>
                  )}

                  {!alt.acknowledged && (
                    <button
                      onClick={() => handleAcknowledge(alt.id)}
                      className="mt-3 w-full flex items-center justify-center gap-1.5 bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-200 text-xs font-semibold py-1 rounded transition duration-150"
                    >
                      <CheckCircle className="h-3 w.5 text-emerald-400" />
                      Acknowledge Alert
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Slide-in Live Toast notifications for new Critical alerts */}
      <div className="fixed bottom-4 right-4 space-y-2 z-[9999] pointer-events-none">
        {activeAlerts.slice(0, 3).map((alt) => (
          <div
            key={`toast-${alt.id}`}
            className="pointer-events-auto w-96 p-4 rounded-xl border border-rose-800 bg-slate-900 bg-opacity-95 backdrop-blur shadow-2xl flex gap-3 animate-slide-in shadow-rose-950/20"
          >
            <div className="p-2 rounded-lg bg-rose-500 bg-opacity-15 h-fit text-rose-400">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-start">
                <h4 className="font-bold text-slate-100 text-sm">Critical Breach Alert!</h4>
                <span className="text-[10px] text-slate-500">Shipment #{alt.shipment_id}</span>
              </div>
              <p className="text-xs text-slate-400 mt-1">{alt.message}</p>
              <button
                onClick={() => handleAcknowledge(alt.id)}
                className="mt-2.5 flex items-center gap-1 text-[11px] font-semibold text-rose-400 hover:text-rose-300 transition"
              >
                Acknowledge Now &rarr;
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
