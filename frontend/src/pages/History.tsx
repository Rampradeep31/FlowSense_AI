import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LuHistory, LuSearch, LuTrendingUp, LuGift, LuTrash2, 
  LuCalendar, LuMapPin, LuShieldAlert, LuCheck 
} from 'react-icons/lu';

interface PredictionLog {
  id: number;
  origin: string;
  destination: string;
  distance: number;
  fuel_price: number;
  month: string;
  predicted_freight_cost: number;
  confidence_score: number;
  created_at: string;
}

interface RecommendationLog {
  id: number;
  total_landed_cost: number;
  product_cost: number;
  predicted_freight_cost: number;
  risk_premium: number;
  created_at: string;
  prediction: {
    origin: string;
    destination: string;
    distance: number;
    fuel_price: number;
    month: string;
  };
  supplier: {
    name: string;
    country: string;
    product_name: string;
  };
}

const History: React.FC = () => {
  const [predictions, setPredictions] = useState<PredictionLog[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState<'predict' | 'recommend'>('predict');
  
  // Delete states
  const [deleteType, setDeleteType] = useState<'predict' | 'recommend' | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/history', {
        params: { search: search || undefined }
      });
      setPredictions(response.data.predictions);
      setRecommendations(response.data.recommendations);
    } catch (err) {
      setError("Failed to fetch history logs.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [search]);

  const handleDeleteConfirm = (type: 'predict' | 'recommend', id: number) => {
    setDeleteType(type);
    setDeleteId(id);
  };

  const executeDelete = async () => {
    if (!deleteType || !deleteId) return;
    try {
      if (deleteType === 'predict') {
        await axios.delete(`/api/history/prediction/${deleteId}`);
      } else {
        await axios.delete(`/api/history/recommendation/${deleteId}`);
      }
      setDeleteId(null);
      setDeleteType(null);
      fetchHistory();
    } catch (err) {
      setError("Deletion failed. Please try again.");
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold font-outfit text-slate-800">System Audit Logs</h2>
          <p className="text-sm text-slate-500">History of cost evaluations, predictions, and recommendations.</p>
        </div>
        
        {/* Tab triggers */}
        <div className="bg-slate-200 p-1 rounded-lg flex self-start sm:self-auto border border-slate-200">
          <button
            onClick={() => setActiveTab('predict')}
            className={`px-4 py-1.5 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition-all ${
              activeTab === 'predict' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <LuTrendingUp className="h-3.5 w-3.5" />
            <span>Predictions ({predictions.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('recommend')}
            className={`px-4 py-1.5 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition-all ${
              activeTab === 'recommend' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <LuGift className="h-3.5 w-3.5" />
            <span>Recommendations ({recommendations.length})</span>
          </button>
        </div>
      </div>

      {/* Search Input */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <LuSearch className="h-4 w-4" />
          </div>
          <input
            type="text"
            placeholder={activeTab === 'predict' 
              ? "Search predictions by Origin or Destination..." 
              : "Search recommendations by Supplier name or Route..."}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50 focus:bg-white"
          />
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Grid Display */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          </div>
        ) : activeTab === 'predict' ? (
          /* PREDICTIONS TABLE */
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Route Details</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Distance</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Fuel Price</th>
                  <th className="px-5 py-3 text-center className text-xs font-semibold text-slate-500 uppercase">Month</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Predicted Cost</th>
                  <th className="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase">Confidence</th>
                  <th className="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Timestamp</th>
                  <th className="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {predictions.length > 0 ? (
                  predictions.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-55/50 transition-colors">
                      <td className="px-5 py-4 whitespace-nowrap text-sm font-medium text-slate-800">
                        <span className="flex items-center"><LuMapPin className="h-4 w-4 text-slate-400 mr-1.5" /> {p.origin} → {p.destination}</span>
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-slate-600 text-right">
                        {p.distance} km
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-slate-600 text-right">
                        ₹{p.fuel_price.toFixed(2)}/L
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-center text-slate-600">
                        {p.month}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-slate-850 font-bold text-right text-blue-600">
                        ₹{p.predicted_freight_cost.toLocaleString()}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-center font-semibold text-emerald-600">
                        {p.confidence_score.toFixed(2)}%
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-xs text-slate-400">
                        {new Date(p.created_at).toLocaleString()}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-center">
                        <button 
                          onClick={() => handleDeleteConfirm('predict', p.id)} 
                          className="text-slate-400 hover:text-red-650 p-1.5 rounded hover:bg-slate-100 transition-colors"
                          title="Delete predictions run log"
                        >
                          <LuTrash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="px-5 py-8 text-center text-slate-400 text-sm">
                      No prediction logs found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        ) : (
          /* RECOMMENDATIONS TABLE */
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Recommended Partner</th>
                  <th className="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Target Route</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Product Cost</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Freight Cost</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase">Risk Premium</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase font-bold">Landed Cost</th>
                  <th className="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase">Timestamp</th>
                  <th className="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recommendations.length > 0 ? (
                  recommendations.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-55/50 transition-colors">
                      <td className="px-5 py-4 whitespace-nowrap text-sm font-medium text-slate-800">
                        <div>
                          <p className="font-bold text-slate-800">{r.supplier?.name || "Deleted Supplier"}</p>
                          <p className="text-xs text-slate-400">{r.supplier?.product_name} • {r.supplier?.country}</p>
                        </div>
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-slate-650 font-medium">
                        {r.prediction ? (
                          <span>{r.prediction.origin} → {r.prediction.destination}</span>
                        ) : (
                          <span className="text-slate-400">Route Deleted</span>
                        )}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-slate-600 text-right">
                        ₹{r.product_cost.toLocaleString()}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-slate-600 text-right">
                        ₹{r.predicted_freight_cost.toLocaleString()}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-slate-600 text-right">
                        ₹{r.risk_premium.toLocaleString()}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm font-bold text-emerald-600 text-right">
                        ₹{r.total_landed_cost.toLocaleString()}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-xs text-slate-400">
                        {new Date(r.created_at).toLocaleString()}
                      </td>
                      <td className="px-5 py-4 whitespace-nowrap text-sm text-center">
                        <button 
                          onClick={() => handleDeleteConfirm('recommend', r.id)} 
                          className="text-slate-400 hover:text-red-650 p-1.5 rounded hover:bg-slate-100 transition-colors"
                          title="Delete recommendation log"
                        >
                          <LuTrash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="px-5 py-8 text-center text-slate-400 text-sm">
                      No optimization recommendation logs found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* CONFIRM DELETE DIALOG */}
      {deleteId && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl p-6 max-w-sm w-full animate-in fade-in zoom-in-95 duration-100">
            <h3 className="font-outfit font-bold text-lg text-slate-800 flex items-center space-x-1">
              <LuShieldAlert className="h-5 w-5 text-red-500" />
              <span>Confirm Deletion</span>
            </h3>
            <p className="text-slate-500 text-sm mt-2">
              Are you sure you want to remove this specific audit record? This cannot be undone.
            </p>
            <div className="flex items-center justify-end mt-6 space-x-3">
              <button 
                onClick={() => { setDeleteId(null); setDeleteType(null); }} 
                className="px-4 py-2 rounded-lg border border-slate-200 text-sm font-semibold text-slate-500 hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={executeDelete} 
                className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-sm font-semibold text-white transition-colors"
              >
                Delete Log
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default History;
