import React, { useState, useEffect } from 'react';
import { Search, Filter, Truck, Calendar, MapPin } from 'lucide-react';

export default function ShipmentList({ selectedShipment, onSelectShipment, refreshTrigger }) {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const fetchShipments = async () => {
    try {
      setLoading(true);
      const resp = await fetch('http://localhost:8000/api/v1/shipments');
      if (resp.ok) {
        const data = await resp.json();
        setShipments(data);
        // Default select the first shipment if none is selected
        if (data.length > 0 && !selectedShipment) {
          onSelectShipment(data[0]);
        }
      }
    } catch (err) {
      console.error('Failed to fetch shipments list:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShipments();
  }, [refreshTrigger]);

  const filteredShipments = shipments.filter((shp) => {
    const matchesSearch =
      shp.origin.toLowerCase().includes(searchQuery.toLowerCase()) ||
      shp.destination.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (shp.product?.name || '').toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === 'all' || shp.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'in_transit':
        return 'bg-blue-500 bg-opacity-15 text-blue-400 border-blue-500/30';
      case 'delayed':
        return 'bg-amber-500 bg-opacity-15 text-amber-400 border-amber-500/30';
      case 'spoiled':
        return 'bg-rose-500 bg-opacity-15 text-rose-400 border-rose-500/30';
      case 'delivered':
        return 'bg-emerald-500 bg-opacity-15 text-emerald-400 border-emerald-500/30';
      default:
        return 'bg-slate-500 bg-opacity-15 text-slate-400 border-slate-500/30';
    }
  };

  const getStatusText = (status) => {
    if (status === 'in_transit') return 'In Transit';
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <div className="glass-card rounded-2xl p-4 flex flex-col h-full border border-slate-800 bg-slate-900/60 backdrop-blur-md">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-slate-100 font-outfit mb-1 flex items-center gap-2">
          <Truck className="h-5 w-5 text-indigo-400" />
          Shipment Tracking
        </h2>
        <p className="text-xs text-slate-400">Select vaccine shipment to monitor live telemetry and risks.</p>
      </div>

      {/* Search and Filters */}
      <div className="space-y-2 mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search by city or product..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-slate-950 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-3.5 w-3.5 text-slate-500" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-lg text-xs py-1.5 px-2 text-slate-400 focus:outline-none focus:border-indigo-500 transition"
          >
            <option value="all">All Statuses</option>
            <option value="in_transit">In Transit</option>
            <option value="delayed">Delayed</option>
            <option value="spoiled">Spoiled</option>
            <option value="delivered">Delivered</option>
          </select>
        </div>
      </div>

      {/* List Container */}
      <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
        {loading && shipments.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500"></div>
          </div>
        ) : filteredShipments.length === 0 ? (
          <div className="text-center py-12 text-sm text-slate-500">
            No matching shipments found.
          </div>
        ) : (
          filteredShipments.map((shp) => {
            const isSelected = selectedShipment && selectedShipment.id === shp.id;
            return (
              <div
                key={shp.id}
                onClick={() => onSelectShipment(shp)}
                className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all duration-200 ${
                  isSelected
                    ? 'bg-indigo-950/20 border-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.15)]'
                    : 'bg-slate-950/30 border-slate-850 hover:border-slate-700 hover:bg-slate-950/50'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-slate-200 text-sm font-outfit">
                    {shp.product?.name || `Product #${shp.product_id}`}
                  </h4>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${getStatusBadgeClass(shp.status)}`}>
                    {getStatusText(shp.status)}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 mb-2">
                  <div className="flex items-center gap-1">
                    <MapPin className="h-3 w-3 text-indigo-400 flex-shrink-0" />
                    <span className="truncate">{shp.origin} &rarr; {shp.destination}</span>
                  </div>
                  <div className="flex items-center gap-1 justify-end">
                    <span className="font-semibold text-slate-300">{shp.quantity} vials</span>
                  </div>
                </div>

                <div className="flex justify-between items-center text-[10px] text-slate-500 border-t border-slate-900 pt-2 mt-2">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {new Date(shp.departure_time).toLocaleDateString(undefined, {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                  <span className="font-mono text-slate-600">ID: SHIP-{shp.id}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
