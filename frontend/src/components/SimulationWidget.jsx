import React, { useState, useEffect } from 'react';
import { Play, TrendingDown, ArrowRight, Star, HelpCircle, Check } from 'lucide-react';

export default function SimulationWidget({ selectedShipment, originalPredictions, onSimulationFinished }) {
  const [carriers, setCarriers] = useState([]);
  const [coldBoxes, setColdBoxes] = useState([]);
  
  // Selection states
  const [selectedCarrier, setSelectedCarrier] = useState('');
  const [selectedColdBox, setSelectedColdBox] = useState('');
  const [selectedTimeOffset, setSelectedTimeOffset] = useState('0'); // in hours

  // Results & recommendations states
  const [simulationResult, setSimulationResult] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [simulating, setSimulating] = useState(false);
  const [loadingRecs, setLoadingRecs] = useState(false);

  // Fetch list of carriers, cold boxes, and recommendations
  useEffect(() => {
    const fetchEntities = async () => {
      try {
        const cResp = await fetch('http://localhost:8000/api/v1/carriers');
        if (cResp.ok) setCarriers(await cResp.json());

        const bResp = await fetch('http://localhost:8000/api/v1/cold-boxes');
        if (bResp.ok) {
          const boxes = await bResp.json();
          // Filter only active boxes
          setColdBoxes(boxes.filter((b) => b.status === 'active'));
        }
      } catch (err) {
        console.error('Failed to load simulation dropdown entities:', err);
      }
    };

    fetchEntities();
  }, []);

  const fetchRecommendations = async () => {
    if (!selectedShipment) return;
    try {
      setLoadingRecs(true);
      const resp = await fetch(`http://localhost:8000/api/v1/simulation/recommendations/${selectedShipment.id}`);
      if (resp.ok) {
        const data = await resp.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
    } finally {
      setLoadingRecs(false);
    }
  };

  useEffect(() => {
    if (!selectedShipment) return;
    // Reset simulation results and selectors on shipment change
    setSimulationResult(null);
    setSelectedCarrier(selectedShipment.carrier_id || '');
    setSelectedColdBox(selectedShipment.cold_box_id || '');
    setSelectedTimeOffset('0');
    
    fetchRecommendations();
  }, [selectedShipment]);

  const handleSimulate = async () => {
    if (!selectedShipment) return;

    try {
      setSimulating(true);
      // Calculate simulated departure time
      let simDepartureTime = null;
      if (selectedTimeOffset !== '0') {
        const origDate = new Date(selectedShipment.departure_time);
        origDate.setHours(origDate.getHours() + parseInt(selectedTimeOffset));
        simDepartureTime = origDate.toISOString();
      }

      const payload = {
        shipment_id: selectedShipment.id,
        carrier_id: selectedCarrier ? parseInt(selectedCarrier) : null,
        cold_box_id: selectedColdBox || null,
        departure_time: simDepartureTime
      };

      const resp = await fetch('http://localhost:8000/api/v1/simulation/what-if', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (resp.ok) {
        const data = await resp.json();
        setSimulationResult(data);
        if (onSimulationFinished) {
          onSimulationFinished(data);
        }
      }
    } catch (err) {
      console.error('Simulation execution failed:', err);
    } finally {
      setSimulating(false);
    }
  };

  // Click recommendation card to apply parameters to selector form
  const applyRecommendation = (rec) => {
    if (rec.type === 'carrier_upgrade' && rec.actionable_details.carrier_id) {
      setSelectedCarrier(rec.actionable_details.carrier_id.toString());
    } else if (rec.type === 'box_upgrade' && rec.actionable_details.cold_box_id) {
      setSelectedColdBox(rec.actionable_details.cold_box_id);
    } else if (rec.type === 'departure_shift' && rec.actionable_details.departure_time) {
      // Find offset in hours
      const orig = new Date(selectedShipment.departure_time);
      const target = new Date(rec.actionable_details.departure_time);
      const hours = Math.round(Math.abs(target - orig) / 36e5);
      setSelectedTimeOffset(hours.toString());
    }
  };

  const getRecTypeLabel = (type) => {
    if (type === 'carrier_upgrade') return 'Carrier Upgrade';
    if (type === 'box_upgrade') return 'Container Upgrade';
    return 'Schedule Shift';
  };

  const getRecTypeColorClass = (type) => {
    if (type === 'carrier_upgrade') return 'bg-indigo-500 bg-opacity-20 text-indigo-400 border-indigo-500/20';
    if (type === 'box_upgrade') return 'bg-emerald-500 bg-opacity-20 text-emerald-400 border-emerald-500/20';
    return 'bg-amber-500 bg-opacity-20 text-amber-400 border-amber-500/20';
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      {/* What-If Simulator Panel */}
      <div className="glass-card rounded-2xl p-4 border border-slate-800 bg-slate-900/60 backdrop-blur-md">
        <h3 className="text-sm font-bold text-slate-200 font-outfit mb-3 flex items-center gap-1.5">
          <Play className="h-4 w-4 text-indigo-400" />
          What-If Scenario Simulator
        </h3>

        {/* Configuration inputs */}
        <div className="space-y-4">
          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-500 mb-1.5">Logistics Carrier</label>
            <select
              value={selectedCarrier}
              onChange={(e) => setSelectedCarrier(e.target.value)}
              className="w-full bg-slate-950 border border-slate-850 rounded-xl text-xs py-2 px-3 text-slate-300 focus:outline-none focus:border-indigo-500"
            >
              <option value="">Select Carrier</option>
              {carriers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} (Reliability: {c.reliability_pct}%)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-500 mb-1.5">Insulated Cold Box</label>
            <select
              value={selectedColdBox}
              onChange={(e) => setSelectedColdBox(e.target.value)}
              className="w-full bg-slate-950 border border-slate-850 rounded-xl text-xs py-2 px-3 text-slate-300 focus:outline-none focus:border-indigo-500"
            >
              <option value="">Select Cold Box</option>
              {coldBoxes.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.id} ({b.model} - Age: {b.age_months}m)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-500 mb-1.5">Departure Schedule Shift</label>
            <select
              value={selectedTimeOffset}
              onChange={(e) => setSelectedTimeOffset(e.target.value)}
              className="w-full bg-slate-950 border border-slate-850 rounded-xl text-xs py-2 px-3 text-slate-300 focus:outline-none focus:border-indigo-500"
            >
              <option value="0">On-time (Original departure schedule)</option>
              <option value="6">+6 Hours Shift</option>
              <option value="12">+12 Hours Shift</option>
              <option value="24">+24 Hours Shift</option>
            </select>
          </div>

          <button
            onClick={handleSimulate}
            disabled={simulating}
            className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-lg shadow-indigo-950/30"
          >
            {simulating ? 'Running Engine...' : 'Run Simulation'}
          </button>
        </div>

        {/* Simulation Output comparisons */}
        {simulationResult && (
          <div className="mt-4 pt-4 border-t border-slate-800 text-xs">
            <h4 className="font-bold text-slate-300 mb-2">Simulated Outcome Comparison</h4>
            
            <div className="grid grid-cols-2 gap-4">
              {/* Delay Comparison */}
              <div className="p-2.5 rounded-lg bg-slate-950/50 border border-slate-850">
                <span className="text-[10px] text-slate-500 block mb-1">Transit Delay Change</span>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-300">{simulationResult.simulated_delay_hours}h</span>
                  <span className={`text-[10px] font-semibold flex items-center gap-0.5 ${
                    simulationResult.delay_reduction_hours > 0 ? 'text-emerald-400' : simulationResult.delay_reduction_hours < 0 ? 'text-rose-400' : 'text-slate-500'
                  }`}>
                    {simulationResult.delay_reduction_hours > 0 ? '-' : '+'}{Math.abs(simulationResult.delay_reduction_hours)}h
                  </span>
                </div>
              </div>

              {/* Spoilage Risk Comparison */}
              <div className="p-2.5 rounded-lg bg-slate-950/50 border border-slate-850">
                <span className="text-[10px] text-slate-500 block mb-1">Spoilage Risk Change</span>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-300">{Math.round(simulationResult.simulated_spoilage_probability * 100)}%</span>
                  <span className={`text-[10px] font-semibold flex items-center gap-0.5 ${
                    simulationResult.spoilage_reduction_pct > 0 ? 'text-emerald-400' : simulationResult.spoilage_reduction_pct < 0 ? 'text-rose-400' : 'text-slate-500'
                  }`}>
                    {simulationResult.spoilage_reduction_pct > 0 ? 'saved ' : '+'}{Math.abs(simulationResult.spoilage_reduction_pct).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Decision Support Recommendations Panel */}
      <div className="glass-card rounded-2xl p-4 border border-slate-800 bg-slate-900/60 backdrop-blur-md flex flex-col h-full">
        <div>
          <h3 className="text-sm font-bold text-slate-200 font-outfit mb-1 flex items-center gap-1.5">
            <Star className="h-4 w-4 text-emerald-400" />
            Decision Recommendations
          </h3>
          <p className="text-[11px] text-slate-400 mb-3">AI-driven choices to minimize temperature exposure and delays.</p>
        </div>

        <div className="flex-1 overflow-y-auto space-y-2.5 max-h-[280px] pr-1">
          {loadingRecs ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-emerald-500"></div>
            </div>
          ) : recommendations.length === 0 ? (
            <div className="text-center py-12 text-xs text-slate-500">
              No optimizations required; current settings are optimal.
            </div>
          ) : (
            recommendations.map((rec, idx) => (
              <div
                key={`rec-${idx}`}
                onClick={() => applyRecommendation(rec)}
                className="p-3 rounded-xl border border-slate-850 bg-slate-950/30 hover:border-emerald-500/40 hover:bg-slate-950/60 cursor-pointer transition duration-150 flex items-start justify-between gap-3 group"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border capitalize ${getRecTypeColorClass(rec.type)}`}>
                      {getRecTypeLabel(rec.type)}
                    </span>
                    <span className="text-[10px] text-slate-500 flex items-center gap-0.5">
                      <TrendingDown className="h-3 w-3 text-emerald-400" />
                      Risk Saver
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-snug">{rec.description}</p>
                </div>
                
                {/* Reduction metrics badges */}
                <div className="text-right flex flex-col justify-between h-full min-w-[70px]">
                  {rec.predicted_spoilage_reduction_pct > 0 && (
                    <div className="text-[11px] font-bold text-emerald-400">
                      -{rec.predicted_spoilage_reduction_pct}% Spoil
                    </div>
                  )}
                  {rec.predicted_delay_reduction_hours > 0 && (
                    <div className="text-[10px] text-slate-400 font-semibold">
                      -{rec.predicted_delay_reduction_hours}h Delay
                    </div>
                  )}
                  <span className="text-[10px] text-indigo-400 font-bold group-hover:translate-x-1 transition duration-150 flex items-center justify-end mt-2">
                    Apply <ArrowRight className="h-3 w-3 inline ml-0.5" />
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}
