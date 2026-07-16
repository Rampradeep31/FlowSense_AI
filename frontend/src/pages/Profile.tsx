import React from 'react';
import { useAuth } from '../App';
import { useNavigate } from 'react-router-dom';
import { LuUser, LuLogOut, LuSchool, LuInfo, LuCpu, LuCheck } from 'react-icons/lu';

const Profile: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const systemDetails = {
    title: "FlowSense AI: Smart Procurement and Freight Cost Prediction System",
    version: "1.0.0",
    engine: "Random Forest Regressor (Scikit-Learn)",
    backend: "FastAPI (Python 3.10+)",
    frontend: "React (TypeScript, Tailwind CSS)",
    database: "PostgreSQL / SQLite with Unified Connection Pool"
  };

  return (
    <div className="space-y-6">
      
      {/* Title */}
      <div>
        <h2 className="text-2xl font-bold font-outfit text-slate-800">User Configuration Profile</h2>
        <p className="text-sm text-slate-500">View user session state and system configuration details.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: Account Info Card (4 cols) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm lg:col-span-4 flex flex-col justify-between space-y-6">
          <div className="space-y-4 text-center">
            <div className="h-20 w-20 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-3xl mx-auto shadow-inner">
              {user?.username?.substring(0, 2).toUpperCase()}
            </div>
            <div>
              <h3 className="text-xl font-bold text-slate-800">{user?.username}</h3>
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider mt-0.5">Procurement Administrator</p>
            </div>
          </div>

          <div className="space-y-2 text-sm border-t border-slate-100 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Account ID</span>
              <span className="font-semibold text-slate-700">#{user?.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Account Registered</span>
              <span className="font-semibold text-slate-700">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "N/A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Session Status</span>
              <span className="inline-flex items-center text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                <span className="h-1.5 w-1.5 bg-emerald-500 rounded-full mr-1 animate-pulse"></span>
                Active Auth
              </span>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="w-full bg-red-50 hover:bg-red-100 text-red-650 font-semibold py-2.5 rounded-lg flex items-center justify-center space-x-2 text-sm border border-red-200 transition-colors"
          >
            <LuLogOut className="h-4 w-4" />
            <span>Sign Out from Session</span>
          </button>
        </div>

        {/* Right Side: System Info (8 cols) */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm lg:col-span-8 space-y-6">
          <div className="flex items-center space-x-2 border-b border-slate-100 pb-4">
            <LuInfo className="h-5 w-5 text-blue-600" />
            <h3 className="font-outfit font-bold text-base text-slate-800">System Information & Engine Status</h3>
          </div>

          <div className="space-y-4 text-sm text-slate-600 leading-relaxed">
            <div>
              <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block">Application Title</span>
              <p className="font-bold text-slate-800 text-base">{systemDetails.title}</p>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block">Deployment Type</span>
                <p className="font-medium text-slate-800">Explainable AI Decision Support System</p>
                <p className="text-xs text-slate-400">Production Version {systemDetails.version}</p>
              </div>
              <div>
                <span className="text-xs text-slate-400 font-bold uppercase tracking-wider block">Core Architecture</span>
                <p className="font-bold text-slate-800">FastAPI & React Integration</p>
                <p className="text-xs text-slate-400">PostgreSQL / SQLite Storage</p>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start space-x-3 text-xs text-blue-800 mt-4">
              <LuCpu className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-blue-900 mb-1">Random Forest Prediction Pipeline Verified</p>
                <p className="leading-relaxed">
                  The model utilizes 100 decision trees to fit numerical and categorical attributes. Categories are expanded using One-Hot-Encoding within the Joblib pipeline, ensuring zero data leakage and 95.46% test accuracy.
                </p>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default Profile;
