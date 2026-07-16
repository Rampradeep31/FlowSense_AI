import React, { useState } from 'react';
import axios from 'axios';
import { 
  LuTrendingUp, LuMapPin, LuCalendar, LuGauge, LuLayers, 
  LuShieldAlert, LuCheck, LuInfo 
} from 'react-icons/lu';

interface PredictionResult {
  id: number;
  predicted_freight_cost: number;
  confidence_score: number;
  origin: string;
  destination: string;
  distance: number;
  fuel_price: number;
  month: string;
}

const Predictor: React.FC = () => {
  // Input fields
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [distance, setDistance] = useState('');
  const [fuelPrice, setFuelPrice] = useState('95.50'); // Reasonable default in Maharashtra
  const [month, setMonth] = useState('January');
  
  // Results & Loading
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Common routes preset to make testing fast during mini-project viva
  const routePresets = [
    { name: "Mumbai to Pune (150 km)", origin: "Mumbai", destination: "Pune", distance: "150" },
    { name: "Mumbai to Nashik (170 km)", origin: "Mumbai", destination: "Nashik", distance: "170" },
    { name: "Mumbai to Nagpur (800 km)", origin: "Mumbai", destination: "Nagpur", distance: "800" },
    { name: "Pune to Nagpur (710 km)", origin: "Pune", destination: "Nagpur", distance: "710" },
    { name: "Nashik to Aurangabad (190 km)", origin: "Nashik", destination: "Aurangabad", distance: "190" },
    { name: "Kolhapur to Mumbai (380 km)", origin: "Kolhapur", destination: "Mumbai", distance: "380" }
  ];

  const handleApplyPreset = (preset: typeof routePresets[0]) => {
    setOrigin(preset.origin);
    setDestination(preset.destination);
    setDistance(preset.distance);
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!origin || !destination || !distance || !fuelPrice || !month) {
      setError("Please fill in all input variables.");
      return;
    }
    if (origin.trim().toLowerCase() === destination.trim().toLowerCase()) {
      setError("Origin and Destination cannot be the same city.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('/api/predict', {
        origin,
        destination,
        distance: parseFloat(distance),
        fuel_price: parseFloat(fuelPrice),
        month
      });
      setResult(response.data);
    } catch (err) {
      setError("Prediction failed. Make sure all values are positive and backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold font-outfit text-slate-800">AI Freight Cost Predictor</h2>
        <p className="text-sm text-slate-500">
          Utilize Random Forest Regression to estimate freight costs based on geographical, fuel, and seasonal parameters.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: Form */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm lg:col-span-7 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <h3 className="font-outfit font-bold text-base text-slate-800">Estimation Input Variables</h3>
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded">Random Forest Model v1.0</span>
          </div>

          {/* Quick Preset Badges */}
          <div className="space-y-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Quick Route Presets</span>
            <div className="flex flex-wrap gap-2">
              {routePresets.map((preset, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleApplyPreset(preset)}
                  className="text-xs bg-slate-50 border border-slate-200 text-slate-600 px-2.5 py-1.5 rounded-lg hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200 transition-all font-medium"
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handlePredict} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              
              {/* Origin */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Origin City</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <LuMapPin className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={origin}
                    onChange={(e) => setOrigin(e.target.value)}
                    className="pl-9 block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50 focus:bg-white"
                    placeholder="e.g., Mumbai"
                  />
                </div>
              </div>

              {/* Destination */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Destination City</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <LuMapPin className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={destination}
                    onChange={(e) => setDestination(e.target.value)}
                    className="pl-9 block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50 focus:bg-white"
                    placeholder="e.g., Pune"
                  />
                </div>
              </div>

              {/* Distance */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Route Distance (km)</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <LuGauge className="h-4 w-4" />
                  </div>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    required
                    value={distance}
                    onChange={(e) => setDistance(e.target.value)}
                    className="pl-9 block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50 focus:bg-white"
                    placeholder="e.g., 150"
                  />
                </div>
              </div>

              {/* Fuel Price */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Fuel Price (₹/Liter)</label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 text-sm font-semibold">
                    ₹
                  </span>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    required
                    value={fuelPrice}
                    onChange={(e) => setFuelPrice(e.target.value)}
                    className="pl-8 block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50 focus:bg-white"
                    placeholder="e.g., 95.50"
                  />
                </div>
              </div>

              {/* Month */}
              <div className="col-span-2">
                <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Season / Shipment Month</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <LuCalendar className="h-4 w-4" />
                  </div>
                  <select
                    value={month}
                    onChange={(e) => setMonth(e.target.value)}
                    className="pl-9 block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50 focus:bg-white"
                  >
                    {["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"].map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg flex items-start space-x-2 text-sm">
                <LuShieldAlert className="h-5 w-5 flex-shrink-0 mt-0.5 text-red-500" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg flex items-center justify-center space-x-2 text-sm shadow-md shadow-blue-500/10 transition-colors disabled:opacity-50"
            >
              <LuTrendingUp className="h-4 w-4" />
              <span>{loading ? "Running Model Execution..." : "Calculate ML Freight Forecast"}</span>
            </button>
          </form>
        </div>

        {/* Right Side: Prediction Result Display */}
        <div className="lg:col-span-5 flex flex-col">
          {loading ? (
            <div className="flex-1 bg-white border border-slate-200 rounded-xl p-8 shadow-sm flex flex-col items-center justify-center space-y-4">
              <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-slate-500 text-sm font-medium animate-pulse">Running Random Forest Estimator...</p>
            </div>
          ) : result ? (
            <div className="flex-1 bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-6 text-white shadow-lg space-y-6 flex flex-col justify-between">
              
              {/* Card Header */}
              <div className="flex items-center justify-between">
                <span className="text-xs bg-blue-500/20 text-blue-300 font-semibold px-2.5 py-1 rounded border border-blue-500/30">
                  Prediction Succeeded
                </span>
                <LuCheck className="h-6 w-6 text-emerald-400" />
              </div>

              {/* Price Calculation Output */}
              <div className="text-center py-4 border-y border-slate-700/50 space-y-1">
                <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Estimated Freight Cost</p>
                <h4 className="text-4xl font-extrabold text-white">₹{result.predicted_freight_cost.toLocaleString()}</h4>
                <p className="text-xs text-blue-400 flex items-center justify-center mt-1">
                  Confidence Score: <span className="font-bold text-white ml-1">{result.confidence_score.toFixed(2)}%</span>
                </p>
              </div>

              {/* Route Summary */}
              <div className="space-y-3 bg-slate-950/40 p-4 rounded-lg border border-slate-700/30 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Route Path</span>
                  <span className="font-semibold text-slate-200">{result.origin} → {result.destination}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Distance</span>
                  <span className="font-semibold text-slate-200">{result.distance} km</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Fuel Price</span>
                  <span className="font-semibold text-slate-200">₹{result.fuel_price}/L</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Season</span>
                  <span className="font-semibold text-slate-200">{result.month}</span>
                </div>
              </div>

              {/* Save message */}
              <p className="text-slate-400 text-xs text-center flex items-center justify-center">
                <LuLayers className="h-3.5 w-3.5 mr-1" /> Automatically saved to prediction audit logs.
              </p>
            </div>
          ) : (
            <div className="flex-1 bg-white border border-slate-200 rounded-xl p-8 shadow-sm flex flex-col items-center justify-center text-center space-y-4">
              <div className="h-16 w-16 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center">
                <LuInfo className="h-8 w-8" />
              </div>
              <div>
                <h4 className="font-outfit font-bold text-slate-800">Awaiting Input Variables</h4>
                <p className="text-slate-400 text-xs max-w-xs mt-1">
                  Fill in the route parameters on the left and trigger prediction to calculate cost.
                </p>
              </div>
            </div>
          )}
        </div>

      </div>

    </div>
  );
};

export default Predictor;
