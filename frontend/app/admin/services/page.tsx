'use client';

import { useState, useEffect } from 'react';
import { HiOutlineSparkles, HiOutlinePlus, HiOutlinePencilAlt, HiOutlineTrash } from 'react-icons/hi';
import { getServices } from '@/lib/api';
import type { FormattedService } from '@/lib/types';

export default function AdminServicesPage() {
  const [services, setServices] = useState<FormattedService[]>([]);
  const [filterCategory, setFilterCategory] = useState('All Categories');
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    getServices().then(data => {
      // API currently just returns id, name, price. 
      // We map these to the structure expected by the UI.
      const formatted = data.map(s => ({
        id: s.service_id,
        name: s.service_name,
        category: 'General', // default category
        price: `LKR ${s.day_rate}`,
        status: 'Active'
      }));
      setServices(formatted);
    });
  }, []);

  const filteredServices = filterCategory === 'All Categories' 
    ? services 
    : services.filter(service => service.category === filterCategory);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Services & Addons</h1>
          <p className="text-sm text-slate-600 mt-1 font-medium">Manage the service catalogue and pricing for guests.</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-bold rounded-xl shadow-lg transition-colors"
        >
          <HiOutlinePlus size={20} />
          Create New Service
        </button>
      </div>

      <div className="bg-white/80 backdrop-blur-md border border-white/40 shadow-xl shadow-slate-200/50 rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-slate-200/50 bg-slate-50/50 flex justify-between items-center">
          <h3 className="font-bold text-slate-800">Service Catalogue</h3>
          <div className="flex gap-2">
            <select 
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 outline-none"
            >
              <option value="All Categories">All Categories</option>
              {Array.from(new Set(services.map(s => s.category))).map(category => (
                <option key={category} value={category as string}>{category as string}</option>
              ))}
            </select>
          </div>
        </div>

        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-100/30 text-slate-500 text-xs uppercase tracking-wider">
              <th className="p-4 font-bold">Service Name</th>
              <th className="p-4 font-bold">Category</th>
              <th className="p-4 font-bold">Price</th>
              <th className="p-4 font-bold">Status</th>
              <th className="p-4 font-bold text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredServices.map((service) => (
              <tr key={service.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-sky-100 flex items-center justify-center text-sky-600">
                      <HiOutlineSparkles size={20} />
                    </div>
                    <span className="font-bold text-slate-800">{service.name}</span>
                  </div>
                </td>
                <td className="p-4 font-medium text-slate-600">{service.category}</td>
                <td className="p-4 font-black text-slate-800">{service.price}</td>
                <td className="p-4">
                  <span className={`px-2.5 py-1 rounded-md text-xs font-bold ${service.status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-slate-200 text-slate-600'}`}>
                    {service.status}
                  </span>
                </td>
                <td className="p-4 text-right">
                  <div className="flex justify-end gap-2">
                    <button className="p-2 text-slate-400 hover:text-sky-500 hover:bg-sky-50 rounded-lg transition-colors">
                      <HiOutlinePencilAlt size={20} />
                    </button>
                    <button className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                      <HiOutlineTrash size={20} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create Service Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={() => setShowAddModal(false)}></div>
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6 border-b border-slate-100">
              <h3 className="text-xl font-bold text-slate-800">Add New Service</h3>
              <p className="text-sm text-slate-500 mt-1">Create a new service or addon for the catalogue.</p>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Service Name</label>
                <input type="text" placeholder="e.g. Airport Transfer" className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition-all text-sm font-medium" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Category</label>
                  <select className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition-all text-sm font-medium text-slate-700">
                    <option>Wellness</option>
                    <option>Transport</option>
                    <option>Accommodation</option>
                    <option>Food & Beverage</option>
                    <option>Experiences</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Price ($)</label>
                  <input type="text" placeholder="0.00" className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition-all text-sm font-medium" />
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-slate-100 bg-slate-50/50 flex justify-end gap-3">
              <button onClick={() => setShowAddModal(false)} className="px-5 py-2.5 text-sm font-bold text-slate-600 hover:bg-slate-200 rounded-xl transition-colors">
                Cancel
              </button>
              <button onClick={() => setShowAddModal(false)} className="px-5 py-2.5 text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 rounded-xl shadow-md transition-colors">
                Save Service
              </button>
            </div>
          </div>
        </div>
      )}
    </div>

  );
}
