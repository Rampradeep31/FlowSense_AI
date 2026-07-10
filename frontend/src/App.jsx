import React, { useState } from 'react';
import ShipmentList from './components/ShipmentList';
import MapDashboard from './components/MapDashboard';
import PredictivePanel from './components/PredictivePanel';
import SimulationWidget from './components/SimulationWidget';
import AlertCenter from './components/AlertCenter';
import { ShieldAlert, RefreshCw } from 'lucide-react';
import './App.css';

export default function App() {
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [riskCategory, setRiskCategory] = useState('low');
  const [originalPredictions, setOriginalPredictions] = useState(null);
  const [refreshCount, setRefreshCount] = useState(0);

  const handlePredictionLoaded = (data) => {
    setRiskCategory(data.riskCategory);
    setOriginalPredictions(data);
  };

  const handleAlertUpdate = () => {
    // Refresh lists and telemetry when alert events or acknowledgments trigger
    setRefreshCount((prev) => prev + 1);
  };

  const handleSimulationFinished = (simData) => {
    // Optional callback if parent needs to react to simulated outputs
  };

  return (
    <div className="dashboard-container">
      {/* 1. Header */}
      <header className="dashboard-header">
        <div className="flex flex-col">
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-100 font-outfit flex items-center gap-2">
            <span className="text-gradient">FlowSense AI</span>
            <span className="text-[10px] font-semibold bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 px-2 py-0.5 rounded-full uppercase tracking-wider">
              District Portal
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Intelligent Cold Chain Monitoring & Decision Support &bull; Maharashtra Route Control
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full">
            <span className="h-2 w-2 bg-emerald-500 rounded-full animate-pulse"></span>
            Telemetry Stream: Active
          </div>
          
          <button 
            onClick={() => setRefreshCount((prev) => prev + 1)}
            className="p-2 rounded-full bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-300 transition duration-150"
            title="Refresh Dashboard"
          >
            <RefreshCw className="h-4 w-4" />
          </button>

          <AlertCenter onAlertUpdate={handleAlertUpdate} />
        </div>
      </header>

      {/* 2. Main Tracking Grid */}
      <main className="dashboard-grid flex-1">
        {/* Left Column: Shipment List */}
        <section className="h-[600px]">
          <ShipmentList
            selectedShipment={selectedShipment}
            onSelectShipment={setSelectedShipment}
            refreshTrigger={refreshCount}
          />
        </section>

        {/* Center Column: Interactive Route Map */}
        <section className="h-[600px]">
          <MapDashboard
            selectedShipment={selectedShipment}
            riskCategory={riskCategory}
          />
        </section>

        {/* Right Column: Predictive Analytics Panel */}
        <section className="h-[600px] overflow-y-auto pr-1">
          <PredictivePanel
            selectedShipment={selectedShipment}
            onPredictionLoaded={handlePredictionLoaded}
            refreshTrigger={refreshCount}
          />
        </section>
      </main>

      {/* 3. Bottom Simulator Panel */}
      <footer className="mt-2">
        <SimulationWidget
          selectedShipment={selectedShipment}
          originalPredictions={originalPredictions}
          onSimulationFinished={handleSimulationFinished}
        />
      </footer>
    </div>
  );
}
