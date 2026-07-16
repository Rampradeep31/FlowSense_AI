import React from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../App';
import { LuTrendingUp, LuShieldAlert, LuBadgeCheck, LuSettings, LuPlay } from 'react-icons/lu';

const Splash: React.FC = () => {
  const { token } = useAuth();

  // If already logged in, skip splash and go directly to dashboard
  if (token) {
    return <Navigate to="/dashboard" replace />;
  }

  const objectives = [
    { title: "ML Freight Prediction", desc: "Predicts freight charges using Random Forest regression based on origin, destination, distance, fuel prices, and season.", icon: LuTrendingUp, color: "bg-blue-500" },
    { title: "Supplier Risk Auditing", desc: "Calculates risk scores dynamically using quality ratings, delivery delay patterns, and industry experience.", icon: LuShieldAlert, color: "bg-amber-500" },
    { title: "Landed Cost Optimization", desc: "Recommends optimal procurement channels by adding risk premium to standard purchase prices.", icon: LuBadgeCheck, color: "bg-emerald-500" }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col justify-between">
      {/* Navbar decoration */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-slate-800 bg-slate-950/80 sticky top-0 z-50">
        <div className="flex items-center space-x-2">
          <div className="h-9 w-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg">FS</div>
          <span className="font-outfit font-bold text-xl text-white tracking-wide">FlowSense AI</span>
        </div>
        <div className="flex items-center space-x-4">
          <Link to="/login" className="text-sm font-semibold text-slate-300 hover:text-white transition-colors">Log In</Link>
          <Link to="/register" className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded-lg shadow-lg shadow-blue-500/20 transition-all">Sign Up</Link>
        </div>
      </header>

      {/* Main Showcase Hero */}
      <main className="flex-1 flex items-center justify-center py-12 px-6">
        <div className="max-w-5xl w-full text-center space-y-12">
          
          {/* Title & Metadata */}
          <div className="space-y-4">
            <h1 className="font-outfit font-extrabold text-4xl sm:text-5xl md:text-6xl text-white tracking-tight leading-none">
              FlowSense AI: Smart Procurement & <br className="hidden md:inline"/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
                Freight Cost Prediction System
              </span>
            </h1>
            <p className="max-w-2xl mx-auto text-slate-400 text-base sm:text-lg">
              An explainable AI decision support system that optimizes total procurement landed cost by integrating Random Forest cost forecasts and supplier risk premiums.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/login" className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-lg shadow-xl shadow-blue-500/15 transition-all text-base w-full sm:w-auto justify-center">
              <span>Access System</span>
              <LuPlay className="h-4 w-4" />
            </Link>
          </div>

          {/* Project Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
            {objectives.map((obj, i) => (
              <div key={i} className="bg-slate-950/40 border border-slate-800/80 p-6 rounded-2xl text-left hover:border-slate-700/80 transition-all flex flex-col justify-between">
                <div className="space-y-4">
                  <div className={`h-10 w-10 rounded-lg ${obj.color} flex items-center justify-center text-white`}>
                    <obj.icon className="h-5 w-5" />
                  </div>
                  <h3 className="font-outfit font-bold text-lg text-white">{obj.title}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{obj.desc}</p>
                </div>
              </div>
            ))}
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-slate-800 py-6 px-6 text-center text-xs sm:text-sm text-slate-500">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 FlowSense AI. All rights reserved.</p>
          <div className="text-slate-400">
            Intelligent Procurement & Freight Cost Prediction
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Splash;
