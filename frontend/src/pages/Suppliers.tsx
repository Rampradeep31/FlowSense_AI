import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LuSearch, LuPlus, LuPencil, LuTrash2, LuChevronLeft, LuChevronRight, 
  LuX, LuInfo, LuMapPin, LuStar, LuShieldAlert, LuArrowUpDown
} from 'react-icons/lu';

interface Supplier {
  id: number;
  name: string;
  country: string;
  product_name: string;
  product_cost: number;
  delivery_time: number;
  quality_rating: number;
  late_deliveries: number;
  experience: number;
  contact_info: string;
}

const Suppliers: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  
  // Search, filter, page states
  const [search, setSearch] = useState('');
  const [country, setCountry] = useState('');
  const [productName, setProductName] = useState('');
  const [sortBy, setSortBy] = useState('id');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  
  // Modal / Form state
  const [formOpen, setFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  
  // Form fields
  const [name, setName] = useState('');
  const [supCountry, setSupCountry] = useState('');
  const [product, setProduct] = useState('');
  const [cost, setCost] = useState('');
  const [delTime, setDelTime] = useState('');
  const [rating, setRating] = useState('');
  const [lateDel, setLateDel] = useState('');
  const [exp, setExp] = useState('');
  const [contact, setContact] = useState('');
  
  // Delete Dialog state
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchSuppliers = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/suppliers', {
        params: {
          search: search || undefined,
          country: country || undefined,
          product_name: productName || undefined,
          sort_by: sortBy,
          sort_dir: sortDir,
          page,
          limit
        }
      });
      setSuppliers(response.data.suppliers);
      setTotal(response.data.total);
    } catch (err) {
      setError("Failed to fetch suppliers. Please make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, [search, country, productName, sortBy, sortDir, page]);

  const handleOpenAdd = () => {
    setEditingId(null);
    setName('');
    setSupCountry('');
    setProduct('');
    setCost('');
    setDelTime('');
    setRating('');
    setLateDel('');
    setExp('');
    setContact('');
    setError(null);
    setFormOpen(true);
  };

  const handleOpenEdit = (s: Supplier) => {
    setEditingId(s.id);
    setName(s.name);
    setSupCountry(s.country);
    setProduct(s.product_name);
    setCost(s.product_cost.toString());
    setDelTime(s.delivery_time.toString());
    setRating(s.quality_rating.toString());
    setLateDel(s.late_deliveries.toString());
    setExp(s.experience.toString());
    setContact(s.contact_info);
    setError(null);
    setFormOpen(true);
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !supCountry || !product || !cost || !delTime || !rating || !lateDel || !exp || !contact) {
      setError("All fields are required.");
      return;
    }

    const payload = {
      name,
      country: supCountry,
      product_name: product,
      product_cost: parseFloat(cost),
      delivery_time: parseInt(delTime),
      quality_rating: parseFloat(rating),
      late_deliveries: parseInt(lateDel),
      experience: parseInt(exp),
      contact_info: contact
    };

    try {
      if (editingId) {
        await axios.put(`/api/suppliers/${editingId}`, payload);
      } else {
        await axios.post('/api/suppliers', payload);
      }
      setFormOpen(false);
      fetchSuppliers();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Action failed. Check fields values.");
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await axios.delete(`/api/suppliers/${deleteId}`);
      setDeleteId(null);
      fetchSuppliers();
    } catch (err) {
      setError("Failed to delete supplier.");
    }
  };

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortDir('asc');
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      
      {/* Header section */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold font-outfit text-slate-800">Supplier Directory</h2>
          <p className="text-sm text-slate-500">Manage procurement channels, quality records, and contact details.</p>
        </div>
        <button onClick={handleOpenAdd} className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg flex items-center space-x-2 text-sm shadow-md shadow-blue-500/10 transition-colors">
          <LuPlus className="h-4 w-4" />
          <span>Add Supplier</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center gap-4">
        
        {/* Search */}
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <LuSearch className="h-4 w-4" />
          </div>
          <input
            type="text"
            placeholder="Search by supplier name, product or country..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-slate-50 focus:bg-white"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Product Filter */}
          <select 
            value={productName} 
            onChange={(e) => setProductName(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 bg-slate-50"
          >
            <option value="">All Products</option>
            <option value="Lithium-Ion Batteries">Lithium-Ion Batteries</option>
            <option value="API - Paracetamol">API - Paracetamol</option>
            <option value="Solar PV Panels">Solar PV Panels</option>
            <option value="Specialty Steel Alloys">Specialty Steel Alloys</option>
          </select>

          {/* Country Filter */}
          <select 
            value={country} 
            onChange={(e) => setCountry(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 bg-slate-50"
          >
            <option value="">All Countries</option>
            <option value="India">India</option>
            <option value="China">China</option>
            <option value="Germany">Germany</option>
            <option value="Japan">Japan</option>
          </select>
        </div>
      </div>

      {/* Grid Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th onClick={() => handleSort('name')} className="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100">
                  <div className="flex items-center space-x-1"><span>Supplier</span> <LuArrowUpDown className="h-3 w-3"/></div>
                </th>
                <th onClick={() => handleSort('product_name')} className="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100">
                  <div className="flex items-center space-x-1"><span>Product</span> <LuArrowUpDown className="h-3 w-3"/></div>
                </th>
                <th onClick={() => handleSort('product_cost')} className="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100">
                  <div className="flex items-center space-x-1 justify-end"><span>Base Cost</span> <LuArrowUpDown className="h-3 w-3"/></div>
                </th>
                <th onClick={() => handleSort('quality_rating')} className="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100">
                  <div className="flex items-center space-x-1 justify-center"><span>Quality</span> <LuArrowUpDown className="h-3 w-3"/></div>
                </th>
                <th onClick={() => handleSort('delivery_time')} className="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100">
                  <div className="flex items-center space-x-1 justify-center"><span>Delivery Time</span> <LuArrowUpDown className="h-3 w-3"/></div>
                </th>
                <th className="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">Late Orders</th>
                <th className="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">Exp</th>
                <th className="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Contact</th>
                <th className="px-5 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={9} className="px-5 py-8 text-center">
                    <div className="h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  </td>
                </tr>
              ) : suppliers.length > 0 ? (
                suppliers.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-55/50 transition-colors">
                    <td className="px-5 py-4 whitespace-nowrap text-sm font-medium text-slate-800">
                      <div>
                        <p>{s.name}</p>
                        <p className="text-xs text-slate-400 flex items-center mt-0.5"><LuMapPin className="h-3.5 w-3.5 mr-0.5" /> {s.country}</p>
                      </div>
                    </td>
                    <td className="px-5 py-4 whitespace-nowrap text-sm text-slate-600">
                      {s.product_name}
                    </td>
                    <td className="px-5 py-4 whitespace-nowrap text-sm font-semibold text-slate-800 text-right">
                      ₹{s.product_cost.toLocaleString()}
                    </td>
                    <td className="px-5 py-4 whitespace-nowrap text-sm text-center font-semibold text-amber-600">
                      <span className="inline-flex items-center space-x-1">
                        <LuStar className="h-3.5 w-3.5 fill-amber-500 text-amber-500" />
                        <span>{s.quality_rating.toFixed(2)}</span>
                      </span>
                    </td>
                    <td className="px-5 py-4 whitespace-nowrap text-sm text-center text-slate-600">
                      {s.delivery_time} days
                    </td>
                    <td className="px-5 py-4 whitespace-nowrap text-sm text-center text-slate-600">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${s.late_deliveries > 5 ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-600'}`}>
                        {s.late_deliveries}
                      </span>
                    </td>
                    <td className="px-5 py-4 whitespace-nowrap text-sm text-center text-slate-600">
                      {s.experience} yrs
                    </td>
                    <td className="px-5 py-4 text-sm text-slate-500 max-w-xs truncate" title={s.contact_info}>
                      {s.contact_info}
                    </td>
                    <td className="px-5 py-4 whitespace-nowrap text-sm text-center space-x-2">
                      <button onClick={() => handleOpenEdit(s)} className="text-slate-500 hover:text-blue-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors" title="Edit">
                        <LuPencil className="h-4 w-4" />
                      </button>
                      <button onClick={() => setDeleteId(s.id)} className="text-slate-500 hover:text-red-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors" title="Delete">
                        <LuTrash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="px-5 py-8 text-center text-slate-400 text-sm">
                    No suppliers match search filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination bar */}
        {totalPages > 1 && (
          <div className="bg-slate-50 px-5 py-3 border-t border-slate-200 flex items-center justify-between text-sm text-slate-500">
            <div>
              Showing page <span className="font-semibold text-slate-700">{page}</span> of <span className="font-semibold text-slate-700">{totalPages}</span>
            </div>
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))} 
                disabled={page === 1}
                className="p-1 rounded-md border border-slate-300 hover:bg-white disabled:opacity-50 transition-colors"
              >
                <LuChevronLeft className="h-4 w-4" />
              </button>
              <button 
                onClick={() => setPage(p => Math.min(totalPages, p + 1))} 
                disabled={page === totalPages}
                className="p-1 rounded-md border border-slate-300 hover:bg-white disabled:opacity-50 transition-colors"
              >
                <LuChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* CRUD MODAL POPUP FORM */}
      {formOpen && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-lg w-full shadow-2xl overflow-hidden my-8">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
              <h3 className="font-outfit font-bold text-lg text-slate-800">
                {editingId ? "Modify Supplier Credentials" : "Register New Supplier Profile"}
              </h3>
              <button onClick={() => setFormOpen(false)} className="text-slate-400 hover:text-slate-600 transition-colors">
                <LuX className="h-5 w-5" />
              </button>
            </div>

            {error && (
              <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs font-semibold flex items-center space-x-2">
                <LuShieldAlert className="h-4 w-4 text-red-500 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleFormSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Supplier / Corporation Name</label>
                  <input type="text" value={name} onChange={(e)=>setName(e.target.value)} required className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500" placeholder="e.g., Tata Steel"/>
                </div>
                
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Country</label>
                  <input type="text" value={supCountry} onChange={(e)=>setSupCountry(e.target.value)} required className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500" placeholder="e.g., India"/>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Product Name</label>
                  <input type="text" value={product} onChange={(e)=>setProduct(e.target.value)} required className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500" placeholder="e.g., Solar PV Panels"/>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Product Cost (₹)</label>
                  <input type="number" step="0.01" value={cost} onChange={(e)=>setCost(e.target.value)} required className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500" placeholder="e.g., 280000"/>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Delivery Time (days)</label>
                  <input type="number" value={delTime} onChange={(e)=>setDelTime(e.target.value)} required className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500" placeholder="e.g., 5"/>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Quality Rating (1.0 to 5.0)</label>
                  <input type="number" step="0.01" min="1.0" max="5.0" value={rating} onChange={(e)=>setRating(e.target.value)} required className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500" placeholder="e.g., 4.7"/>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Late Deliveries Count</label>
                  <input type="number" value={lateDel} onChange={(e)=>setLateDel(e.target.value)} required className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500" placeholder="e.g., 2"/>
                </div>

                <div className="col-span-2">
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Experience (Years)</label>
                  <input type="number" value={exp} onChange={(e)=>setExp(e.target.value)} required className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500" placeholder="e.g., 8"/>
                </div>

                <div className="col-span-2">
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Contact & Email Information</label>
                  <input type="text" value={contact} onChange={(e)=>setContact(e.target.value)} required className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-blue-500" placeholder="e.g., sales@tata.com | +91 22 2382..."/>
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-100">
                <button type="button" onClick={() => setFormOpen(false)} className="px-4 py-2 rounded-lg border border-slate-200 text-sm font-semibold text-slate-500 hover:bg-slate-50 transition-colors">
                  Cancel
                </button>
                <button type="submit" className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-sm font-semibold text-white transition-colors">
                  {editingId ? "Save Modifications" : "Save Supplier"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CONFIRMATION DIALOG (DELETE) */}
      {deleteId && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl p-6 max-w-sm w-full">
            <h3 className="font-outfit font-bold text-lg text-slate-800">Confirm Deletion</h3>
            <p className="text-slate-500 text-sm mt-2">Are you sure you want to delete this supplier profile? This action cannot be undone.</p>
            <div className="flex items-center justify-end mt-6 space-x-3">
              <button onClick={() => setDeleteId(null)} className="px-4 py-2 rounded-lg border border-slate-200 text-sm font-semibold text-slate-500 hover:bg-slate-50 transition-colors">
                Cancel
              </button>
              <button onClick={handleDelete} className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-sm font-semibold text-white transition-colors">
                Delete Profile
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default Suppliers;
