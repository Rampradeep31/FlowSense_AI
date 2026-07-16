import React, { useState } from 'react';
import axios from 'axios';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip 
} from 'recharts';
import { 
  LuGift, LuShieldAlert, LuBadgeCheck, LuIndianRupee, LuInfo, 
  LuPhone, LuStar, LuTruck, LuArrowRight 
} from 'react-icons/lu';

interface SupplierComparison {
  supplier_id: number;
  supplier_name: string;
  country: string;
  product_cost: number;
  predicted_freight_cost: number;
  risk_score: number;
  risk_level: string;
  risk_premium: number;
  total_landed_cost: number;
  delivery_time: number;
  quality_rating: number;
  experience: number;
}

interface RecommendationResponse {
  recommendation_card: {
    recommended_supplier_name: string;
    country: string;
    product_cost: number;
    predicted_freight_cost: number;
    risk_premium: number;
    total_landed_cost: number;
    savings_vs_average: number;
    contact_info: string;
  };
  cost_breakdown: Array<{ name: string; value: number }>;
  comparison_table: SupplierComparison[];
}

const Recommendations: React.FC = () => {
  // Input states
  const [productName, setProductName] = useState('Lithium-Ion Batteries');
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [distance, setDistance] = useState('');
  const [fuelPrice, setFuelPrice] = useState('95.50');
  const [month, setMonth] = useState('January');

  // Outputs & loading states
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Preset routes
  const routePresets = [
    { name: "Mumbai to Pune (150 km)", origin: "Mumbai", destination: "Pune", distance: "150" },
    { name: "Mumbai to Nagpur (800 km)", origin: "Mumbai", destination: "Nagpur", distance: "800" },
    { name: "Kolhapur to Mumbai (380 km)", origin: "Kolhapur", destination: "Mumbai", distance: "380" }
  ];

  const handleApplyPreset = (preset: typeof routePresets[0]) => {
    setOrigin(preset.origin);
    setDestination(preset.destination);
    setDistance(preset.distance);
  };

  const handleOptimize = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!productName || !origin || !destination || !distance || !fuelPrice || !month) {
      setError("Please fill in all search details.");
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
      const response = await axios.get('/api/recommendation', {
        params: {
          product_name: productName,
          origin,
          destination,
          distance: parseFloat(distance),
          fuel_price: parseFloat(fuelPrice),
          month
        }
      });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Recommendation analysis failed. Please verify inputs or add matching suppliers.");
    } finally {
      setLoading(false);
    }
  };

  const CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b']; // Blue, Emerald, Amber

  return (
    <div className="space-y-6">
      
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold font-outfit text-slate-800">Smart Recommendation Engine</h2>
        <p className="text-sm text-slate-500">
          Rank suppliers by total landed cost ($ProductCost + PredictedFreight + RiskPremium$) to optimize procurement budgets.
        </p>
      </div>

      {/* Input panel & Preset */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
        <form onSubmit={handleOptimize} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Product Select */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Target Product</label>
            <select
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              className="block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50"
            >
              <option value="Lithium-Ion Batteries">Lithium-Ion Batteries</option>
              <option value="API - Paracetamol">API - Paracetamol</option>
              <option value="Solar PV Panels">Solar PV Panels</option>
              <option value="Specialty Steel Alloys">Specialty Steel Alloys</option>
            </select>
          </div>

          {/* Origin */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Origin City</label>
            <input
              type="text"
              required
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              className="block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50"
              placeholder="e.g., Mumbai"
            />
          </div>

          {/* Destination */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Destination City</label>
            <input
              type="text"
              required
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50"
              placeholder="e.g., Pune"
            />
          </div>

          {/* Distance */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Distance (km)</label>
            <input
              type="number"
              step="0.1"
              required
              value={distance}
              onChange={(e) => setDistance(e.target.value)}
              className="block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50"
              placeholder="e.g., 150"
            />
          </div>

          {/* Fuel Price */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Fuel Price (₹/L)</label>
            <input
              type="number"
              step="0.01"
              required
              value={fuelPrice}
              onChange={(e) => setFuelPrice(e.target.value)}
              className="block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50"
            />
          </div>

          {/* Month */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Month of Cargo</label>
            <select
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              className="block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50"
            >
              {["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"].map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>

          {/* Preset Buttons */}
          <div className="md:col-span-2 flex items-center space-x-2 text-xs">
            <span className="text-slate-400 font-semibold">Presets:</span>
            {routePresets.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleApplyPreset(preset)}
                className="bg-slate-100 hover:bg-blue-50 hover:text-blue-600 px-2 py-1 rounded border border-slate-200 transition-colors"
              >
                {preset.name}
              </button>
            ))}
          </div>

          {/* Submit button */}
          <div className="flex items-end justify-end">
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2.5 rounded-lg flex items-center space-x-2 text-sm shadow-md shadow-blue-500/10 transition-colors disabled:opacity-50 w-full justify-center"
            >
              <LuGift className="h-4 w-4" />
              <span>{loading ? "Optimizing Landed Costs..." : "Calculate Best Supplier"}</span>
            </button>
          </div>
        </form>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs font-semibold flex items-center space-x-2">
            <LuShieldAlert className="h-4 w-4 text-red-500 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Loading Block */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-12 bg-white rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="h-10 w-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-500 text-sm animate-pulse">Running route predictions and supplier risk matrix solver...</p>
        </div>
      )}

      {/* Results Block */}
      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* 1. Best Supplier Recommendation Card (left 7 cols) */}
            <div className="bg-slate-900 text-white p-6 rounded-xl shadow-lg lg:col-span-7 flex flex-col justify-between border border-slate-800">
              <div className="space-y-6">
                {/* Badge Header */}
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Optimal Choice Recommended
                  </span>
                  <LuBadgeCheck className="h-8 w-8 text-emerald-400" />
                </div>

                {/* Main Details */}
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest block">Recommended Supplier</span>
                  <h3 className="text-3xl font-extrabold font-outfit text-white leading-tight">
                    {result.recommendation_card.recommended_supplier_name}
                  </h3>
                  <p className="text-sm text-slate-400 flex items-center">
                    Origin Country: <span className="font-semibold text-slate-200 ml-1">{result.recommendation_card.country}</span>
                  </p>
                </div>

                {/* Landed Cost details */}
                <div className="grid grid-cols-2 gap-4 py-4 border-y border-slate-800 text-sm">
                  <div>
                    <span className="text-slate-400 block text-xs">Total Landed Cost</span>
                    <span className="text-2xl font-bold text-emerald-400">₹{result.recommendation_card.total_landed_cost.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-xs">Procurement Savings</span>
                    <span className="text-2xl font-bold text-blue-400">₹{result.recommendation_card.savings_vs_average.toLocaleString()}</span>
                  </div>
                </div>

                {/* Contact info */}
                <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800 flex items-center space-x-3 text-sm">
                  <LuPhone className="h-5 w-5 text-blue-400 flex-shrink-0" />
                  <span className="text-slate-300 truncate" title={result.recommendation_card.contact_info}>
                    {result.recommendation_card.contact_info}
                  </span>
                </div>
              </div>
            </div>

            {/* 2. Landed Cost Breakdown Chart (right 5 cols) */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm lg:col-span-5 flex flex-col justify-between">
              <h3 className="font-outfit font-bold text-slate-800 text-base mb-2">Total Landed Cost Breakdown</h3>
              
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={result.cost_breakdown}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={65}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {result.cost_breakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip formatter={(val) => `₹${Number(val).toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Chart Legend list */}
              <div className="space-y-1 mt-2 text-xs">
                {result.cost_breakdown.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <span className="flex items-center text-slate-500">
                      <span className="h-2 w-2 rounded-full mr-2" style={{ backgroundColor: CHART_COLORS[idx] }}></span>
                      {item.name}
                    </span>
                    <span className="font-semibold text-slate-800">₹{item.value.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* 3. Supplier Comparison Table */}
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden space-y-4">
            <div className="px-5 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
              <h3 className="font-outfit font-bold text-slate-800 text-base">Procurement Channel Comparison</h3>
              <span className="text-xs text-slate-400">Lower Landed Cost is Recommended</span>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead>
                  <tr className="bg-slate-55/30">
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Supplier</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Product Cost</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Freight Cost</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase">Risk Level</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Risk Premium</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Landed Cost</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase font-semibold">Match</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {result.comparison_table.map((row) => {
                    const isRecommended = row.supplier_name === result.recommendation_card.recommended_supplier_name;
                    return (
                      <tr 
                        key={row.supplier_id} 
                        className={`hover:bg-slate-55/35 transition-colors ${isRecommended ? 'bg-blue-50/50 font-semibold' : ''}`}
                      >
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-slate-800">
                          <div>
                            <p className={isRecommended ? 'text-blue-800 font-bold' : ''}>{row.supplier_name}</p>
                            <p className="text-xs text-slate-400">{row.country} • Quality: {row.quality_rating}/5.0 • Exp: {row.experience} yrs</p>
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-slate-600 text-right">
                          ₹{row.product_cost.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-slate-600 text-right">
                          ₹{row.predicted_freight_cost.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-center">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                            row.risk_level === 'Low' ? 'bg-emerald-100 text-emerald-800' :
                            row.risk_level === 'Medium' ? 'bg-amber-100 text-amber-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {row.risk_level} ({row.risk_score})
                          </span>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-slate-600 text-right">
                          ₹{row.risk_premium.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm font-bold text-slate-800 text-right">
                          ₹{row.total_landed_cost.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-center">
                          {isRecommended ? (
                            <span className="inline-flex items-center text-xs bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">
                              Best
                            </span>
                          ) : (
                            <span className="text-slate-400">-</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default Recommendations;
