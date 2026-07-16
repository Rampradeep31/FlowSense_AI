import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { 
  LuUsers, LuTrendingUp, LuShieldAlert, LuAward, LuClock, 
  LuStar, LuMapPin, LuTrendingDown 
} from 'react-icons/lu';

interface DashboardData {
  summary: {
    total_suppliers: number;
    total_predictions: number;
    avg_freight_cost: number;
    avg_risk_score: number;
    recommended_supplier: string;
  };
  recent_activities: Array<{
    id: number;
    action: string;
    timestamp: string;
  }>;
  freight_chart: Array<{
    month: string;
    avg_predicted_cost: number;
  }>;
  risk_chart: Array<{
    risk_level: string;
    count: number;
  }>;
  top_suppliers: Array<{
    id: number;
    name: string;
    country: string;
    product_name: string;
    product_cost: number;
    quality_rating: number;
  }>;
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await axios.get('/api/dashboard');
        setData(response.data);
      } catch (err) {
        setError("Failed to fetch dashboard metrics. Please refresh.");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <div className="h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-500 font-medium animate-pulse">Analyzing logistics metadata...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl text-center">
        {error || "No dashboard data available."}
      </div>
    );
  }

  // Pie chart colors
  const COLORS = ['#10b981', '#f59e0b', '#ef4444']; // Emerald (Low), Amber (Medium), Red (High)

  return (
    <div className="space-y-6">
      
      {/* 1. Header Block */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold font-outfit text-slate-800">Procurement Decision Analytics</h2>
          <p className="text-sm text-slate-500">Real-time overview of supplier channels, risk profiles, and freight rates.</p>
        </div>
        <div className="text-xs text-slate-400 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200 self-start md:self-auto">
          Last Updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* 2. KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
        
        {/* Suppliers */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="h-12 w-12 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0">
            <LuUsers className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Suppliers</p>
            <h3 className="text-2xl font-bold text-slate-800">{data.summary.total_suppliers}</h3>
          </div>
        </div>

        {/* Predictions */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="h-12 w-12 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0">
            <LuTrendingUp className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Predictions Run</p>
            <h3 className="text-2xl font-bold text-slate-800">{data.summary.total_predictions}</h3>
          </div>
        </div>

        {/* Average Freight Cost */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="h-12 w-12 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0 flex-col">
            <span className="font-bold text-xs">Rs.</span>
          </div>
          <div className="truncate">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Freight Cost</p>
            <h3 className="text-2xl font-bold text-slate-800 truncate">₹{data.summary.avg_freight_cost.toLocaleString()}</h3>
          </div>
        </div>

        {/* Average Risk Score */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="h-12 w-12 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center flex-shrink-0">
            <LuShieldAlert className="h-6 w-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Risk Score</p>
            <h3 className="text-2xl font-bold text-slate-800">{data.summary.avg_risk_score} / 100</h3>
          </div>
        </div>

        {/* Recommended Supplier */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="h-12 w-12 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center flex-shrink-0">
            <LuAward className="h-6 w-6" />
          </div>
          <div className="truncate">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Top Recommended</p>
            <h3 className="text-lg font-bold text-slate-800 truncate" title={data.summary.recommended_supplier}>
              {data.summary.recommended_supplier}
            </h3>
          </div>
        </div>
      </div>

      {/* 3. Charts Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Monthly Predicted Freight Chart (Bar Chart) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm lg:col-span-2 space-y-4">
          <h3 className="font-outfit font-bold text-base text-slate-800">Average Predicted Freight Cost vs Month</h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.freight_chart} margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <YAxis tickLine={false} axisLine={false} tickFormatter={(val) => `₹${val/1000}k`} tick={{ fontSize: 12, fill: '#64748b' }} />
                <Tooltip 
                  formatter={(val: number) => [`₹${val.toLocaleString()}`, "Avg Freight"]} 
                  contentStyle={{ backgroundColor: '#1e293b', color: '#fff', borderRadius: '8px', border: 'none' }}
                />
                <Bar dataKey="avg_predicted_cost" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Supplier Risk Profile Chart (Pie Chart) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
          <h3 className="font-outfit font-bold text-base text-slate-800">Supplier Risk Profiles</h3>
          <div className="h-64 w-full flex items-center justify-center">
            {data.summary.total_suppliers > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.risk_chart}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="count"
                    nameKey="risk_level"
                  >
                    {data.risk_chart.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [value, "Suppliers"]} />
                  <Legend verticalAlign="bottom" height={36} iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-400 text-sm">Register suppliers to populate risk data.</p>
            )}
          </div>
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 text-center">
            <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">Risk Level Split</span>
            <div className="flex items-center justify-around mt-1 font-semibold text-sm">
              <span className="text-emerald-600">{data.risk_chart.find(r=>r.risk_level==="Low")?.count || 0} Low</span>
              <span className="text-amber-500">{data.risk_chart.find(r=>r.risk_level==="Medium")?.count || 0} Med</span>
              <span className="text-red-500">{data.risk_chart.find(r=>r.risk_level==="High")?.count || 0} High</span>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Bottom Grid: Activities & Supplier Leaderboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Recent Activity Log */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center space-x-2">
            <LuClock className="h-5 w-5 text-slate-500" />
            <h3 className="font-outfit font-bold text-base text-slate-800">Recent Event History</h3>
          </div>
          
          <div className="flow-root">
            <ul className="-mb-8">
              {data.recent_activities.length > 0 ? (
                data.recent_activities.map((activity, activityIdx) => (
                  <li key={activity.id}>
                    <div className="relative pb-8">
                      {activityIdx !== data.recent_activities.length - 1 ? (
                        <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-slate-200" aria-hidden="true" />
                      ) : null}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center ring-8 ring-white">
                            <span className="h-2 w-2 rounded-full bg-blue-500"></span>
                          </span>
                        </div>
                        <div className="flex-1 min-w-0 pt-1.5 flex justify-between space-x-4">
                          <div>
                            <p className="text-sm text-slate-600">{activity.action}</p>
                          </div>
                          <div className="text-right text-xs whitespace-nowrap text-slate-400">
                            {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))
              ) : (
                <p className="text-slate-400 text-sm py-4 text-center">No predictions or recommendations run yet.</p>
              )}
            </ul>
          </div>
        </div>

        {/* Quality Leaderboard (Top Suppliers) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <LuStar className="h-5 w-5 text-amber-500 fill-amber-400" />
              <h3 className="font-outfit font-bold text-base text-slate-800">Top Quality Suppliers</h3>
            </div>
            <span className="text-xs text-slate-400">Sorted by Rating</span>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead>
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Supplier</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Product</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Quality</th>
                  <th className="px-3 py-2 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Base Cost</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.top_suppliers.length > 0 ? (
                  data.top_suppliers.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-55/50 transition-colors">
                      <td className="px-3 py-3 whitespace-nowrap text-sm font-medium text-slate-800">
                        <div>
                          <p>{s.name}</p>
                          <p className="text-xs text-slate-400 flex items-center"><LuMapPin className="h-3 w-3 mr-0.5" /> {s.country}</p>
                        </div>
                      </td>
                      <td className="px-3 py-3 whitespace-nowrap text-sm text-slate-500">
                        {s.product_name}
                      </td>
                      <td className="px-3 py-3 whitespace-nowrap text-sm text-amber-600 font-semibold flex items-center">
                        <LuStar className="h-3.5 w-3.5 mr-1 fill-amber-500 text-amber-500" />
                        {s.quality_rating.toFixed(2)}
                      </td>
                      <td className="px-3 py-3 whitespace-nowrap text-sm text-slate-800 font-semibold text-right">
                        ₹{s.product_cost.toLocaleString()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="px-3 py-4 text-center text-slate-400 text-sm">
                      No suppliers registered in system yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>

    </div>
  );
};

export default Dashboard;
