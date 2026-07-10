import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts';
import { Shield, Clock, AlertOctagon, HelpCircle, Thermometer } from 'lucide-react';

export default function PredictivePanel({ selectedShipment, onPredictionLoaded, refreshTrigger }) {
  const [delayPred, setDelayPred] = useState(null);
  const [spoilagePred, setSpoilagePred] = useState(null);
  const [tempLogs, setTempLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedShipment) return;

    const fetchPredictiveData = async () => {
      try {
        setLoading(true);
        // 1. Fetch Delay Prediction
        const delayResp = await fetch('http://localhost:8000/api/v1/predictions/delay', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ shipment_id: selectedShipment.id }),
        });
        const delayData = delayResp.ok ? await delayResp.json() : null;

        // 2. Fetch Spoilage Prediction
        const spoilageResp = await fetch('http://localhost:8000/api/v1/predictions/spoilage', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ shipment_id: selectedShipment.id }),
        });
        const spoilageData = spoilageResp.ok ? await spoilageResp.json() : null;

        // 3. Fetch Temperature Telemetry
        const tempResp = await fetch(`http://localhost:8000/api/v1/shipments/${selectedShipment.id}/temperature-log`);
        const tempData = tempResp.ok ? await tempResp.json() : [];

        setDelayPred(delayData);
        setSpoilagePred(spoilageData);
        setTempLogs(tempData);

        if (spoilageData && onPredictionLoaded) {
          onPredictionLoaded({
            riskCategory: spoilageData.risk_category,
            delayData,
            spoilageData
          });
        }
      } catch (err) {
        console.error('Failed to query predictions services:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPredictiveData();
  }, [selectedShipment, refreshTrigger]);

  if (!selectedShipment) {
    return (
      <div className="glass-card rounded-2xl p-6 text-center text-slate-500 border border-slate-800">
        Select a shipment to load predictive analysis.
      </div>
    );
  }

  // Define product temperature bounds
  const tempMin = selectedShipment.product?.temp_min_c ?? 2.0;
  const tempMax = selectedShipment.product?.temp_max_c ?? 8.0;

  const getRiskBadgeClass = (risk) => {
    switch (risk) {
      case 'low':
        return 'bg-emerald-500 bg-opacity-20 text-emerald-400 border-emerald-500/30';
      case 'medium':
        return 'bg-amber-500 bg-opacity-20 text-amber-400 border-amber-500/30';
      case 'high':
        return 'bg-rose-500 bg-opacity-20 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-500 bg-opacity-20 text-slate-400 border-slate-500/30';
    }
  };

  // Format Recharts time ticks
  const formatTimeTick = (tickItem) => {
    try {
      const d = new Date(tickItem);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return tickItem;
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Risk Cards Grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* Delay Prediction Card */}
        <div className="glass-card rounded-2xl p-4 border border-slate-850 bg-slate-900/40 relative overflow-hidden">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-semibold text-slate-400">Transit Delay Estimate</span>
            <Clock className="h-4 w-4 text-indigo-400" />
          </div>
          {loading ? (
            <div className="h-10 w-24 bg-slate-800 rounded animate-pulse my-2"></div>
          ) : delayPred ? (
            <div>
              <div className="text-2xl font-black text-slate-100 font-outfit">
                {delayPred.predicted_delay_hours} hrs
              </div>
              <div className="text-[11px] text-slate-400 mt-1">
                Delay probability: <span className="font-semibold text-slate-200">{Math.round(delayPred.delay_probability * 100)}%</span>
              </div>
            </div>
          ) : (
            <div className="text-sm text-slate-500">Prediction unavailable</div>
          )}
        </div>

        {/* Spoilage Prediction Card */}
        <div className="glass-card rounded-2xl p-4 border border-slate-850 bg-slate-900/40 relative overflow-hidden">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-semibold text-slate-400">Spoilage Probability</span>
            <Shield className="h-4 w-4 text-emerald-400" />
          </div>
          {loading ? (
            <div className="h-10 w-24 bg-slate-800 rounded animate-pulse my-2"></div>
          ) : spoilagePred ? (
            <div className="flex justify-between items-end">
              <div>
                <div className="text-2xl font-black text-slate-100 font-outfit">
                  {Math.round(spoilagePred.spoilage_probability * 100)}%
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  Thermal load risk index
                </div>
              </div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded border capitalize ${getRiskBadgeClass(spoilagePred.risk_category)}`}>
                {spoilagePred.risk_category} Risk
              </span>
            </div>
          ) : (
            <div className="text-sm text-slate-500">Prediction unavailable</div>
          )}
        </div>
      </div>

      {/* 2. Explainable SHAP Attribution list */}
      <div className="glass-card rounded-2xl p-4 border border-slate-800 bg-slate-900/60 backdrop-blur-md">
        <h3 className="text-sm font-bold text-slate-200 font-outfit mb-3 flex items-center gap-1.5">
          <AlertOctagon className="h-4 w-4 text-indigo-400" />
          Explainable AI: SHAP Spoilage Risk Factors
        </h3>

        {loading ? (
          <div className="space-y-2 py-3">
            <div className="h-6 bg-slate-800 rounded animate-pulse w-full"></div>
            <div className="h-6 bg-slate-800 rounded animate-pulse w-2/3"></div>
          </div>
        ) : spoilagePred?.shap_explanations ? (
          <div className="space-y-3">
            {spoilagePred.shap_explanations.map((item, idx) => {
              const val = item.shap_value * 100;
              const isPositive = val >= 0;
              return (
                <div key={`shap-${idx}`} className="text-xs">
                  <div className="flex justify-between mb-1.5">
                    <span className="capitalize text-slate-300 font-medium">{item.feature_name.replace('_', ' ')}</span>
                    <span className={`font-semibold ${isPositive ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {isPositive ? '+' : ''}{val.toFixed(2)}%
                    </span>
                  </div>
                  {/* Contribution bar */}
                  <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden flex relative">
                    {/* Centered zero line */}
                    <div className="absolute left-1/2 w-0.5 h-full bg-slate-700 z-10"></div>
                    {isPositive ? (
                      <div
                        className="h-full bg-gradient-to-r from-rose-500 to-rose-400 rounded-r shadow-[0_0_8px_rgba(244,63,94,0.3)]"
                        style={{ width: `${Math.min(50, val * 2.5)}%`, marginLeft: '50%' }}
                      ></div>
                    ) : (
                      <div
                        className="h-full bg-gradient-to-l from-emerald-500 to-emerald-400 rounded-l shadow-[0_0_8px_rgba(16,185,129,0.3)]"
                        style={{ width: `${Math.min(50, Math.abs(val) * 2.5)}%`, marginLeft: `${50 - Math.min(50, Math.abs(val) * 2.5)}%` }}
                      ></div>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1 leading-snug">{item.description}</p>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-6 text-xs text-slate-500">Explainable factors unavailable</div>
        )}
      </div>

      {/* 3. Temperature Telemetry Log Chart */}
      <div className="glass-card rounded-2xl p-4 border border-slate-800 bg-slate-900/60 backdrop-blur-md">
        <h3 className="text-sm font-bold text-slate-200 font-outfit mb-3 flex items-center gap-1.5">
          <Thermometer className="h-4 w-4 text-emerald-400" />
          IoT Temperature Profile Log
        </h3>

        <div className="h-48 w-full pr-2 text-xs">
          {tempLogs.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={tempLogs}>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatTimeTick}
                  stroke="#475569"
                  tickLine={false}
                />
                <YAxis
                  stroke="#475569"
                  tickLine={false}
                  domain={[
                    Math.min(0, tempMin - 1),
                    Math.max(12, tempMax + 4)
                  ]}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
                  labelFormatter={(lbl) => new Date(lbl).toLocaleTimeString()}
                />
                {/* Safe boundaries references */}
                <ReferenceLine y={tempMax} stroke="#ef4444" strokeDasharray="4 4" label={{ value: 'Max Excursion', fill: '#ef4444', position: 'top', fontSize: 9 }} />
                <ReferenceLine y={tempMin} stroke="#3b82f6" strokeDasharray="4 4" label={{ value: 'Min Limit', fill: '#3b82f6', position: 'bottom', fontSize: 9 }} />
                
                <Line
                  type="monotone"
                  dataKey="temperature_c"
                  name="Temperature (°C)"
                  stroke="#10b981"
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500 text-xs">
              No IoT telemetry readings logged yet. Ensure scheduler is simulating.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
