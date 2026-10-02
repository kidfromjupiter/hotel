'use client';

import { useState, useEffect } from 'react';
import { HiOutlineLocationMarker, HiOutlinePhone, HiOutlineMail, HiOutlinePlus, HiOutlinePencilAlt, HiOutlineTrash } from 'react-icons/hi';
import { getBranches } from '@/lib/api';
import type { AdminBranch } from '@/lib/types';

const BRANCH_METADATA: Record<number, { location: string; phone: string; email: string; rooms: number; status: string }> = {
  1: { location: 'Colombo 03', phone: '+94 11 234 5678', email: 'colombo@skynest.com', rooms: 120, status: 'Active' },
  2: { location: 'Kandy', phone: '+94 81 234 5678', email: 'kandy@skynest.com', rooms: 85, status: 'Active' },
  3: { location: 'Galle', phone: '+94 91 234 5678', email: 'galle@skynest.com', rooms: 40, status: 'Maintenance' },
};

export default function AdminBranchesPage() {
  const [showAddModal, setShowAddModal] = useState(false);
  const [branches, setBranches] = useState<AdminBranch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadBranches() {
      try {
        const data = await getBranches();
        const enrichedBranches = data.map((b) => ({
          id: b.branch_id,
          name: b.branch_name,
          ...(BRANCH_METADATA[b.branch_id] || {
             location: 'Unknown Location',
             phone: 'N/A',
             email: 'contact@skynest.com',
             rooms: 0,
             status: 'Active'
          })
        }));
        setBranches(enrichedBranches);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadBranches();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Branch Management</h1>
          <p className="text-sm text-slate-600 mt-1 font-medium">Manage hotel branches, locations, and contact details.</p>
        </div>
        <button 
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white text-sm font-bold rounded-xl shadow-lg shadow-sky-600/30 transition-colors"
        >
          <HiOutlinePlus size={20} />
          Add New Branch
        </button>
      </div>

      {/* Branches Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {branches.map((branch) => (
          <div key={branch.id} className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/40 shadow-xl shadow-slate-200/50 hover:bg-white/90 transition-all duration-300">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-slate-800">{branch.name}</h3>
                <span className={`inline-block mt-2 px-2.5 py-1 rounded-md text-xs font-bold ${branch.status === 'Active' ? 'bg-emerald-100 text-emerald-700' : 'bg-orange-100 text-orange-700'}`}>
                  {branch.status}
                </span>
              </div>
              <div className="flex gap-2">
                <button className="p-2 text-slate-400 hover:text-sky-500 hover:bg-sky-50 rounded-lg transition-colors">
                  <HiOutlinePencilAlt size={20} />
                </button>
                <button className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                  <HiOutlineTrash size={20} />
                </button>
              </div>
            </div>

            <div className="space-y-3 mt-6 border-t border-slate-200/50 pt-4">
              <div className="flex items-center gap-3 text-slate-600 text-sm font-medium">
                <HiOutlineLocationMarker className="text-slate-400" size={18} />
                {branch.location}
              </div>
              <div className="flex items-center gap-3 text-slate-600 text-sm font-medium">
                <HiOutlinePhone className="text-slate-400" size={18} />
                {branch.phone}
              </div>
              <div className="flex items-center gap-3 text-slate-600 text-sm font-medium">
                <HiOutlineMail className="text-slate-400" size={18} />
                {branch.email}
              </div>
            </div>

            <div className="mt-6 bg-slate-50/50 rounded-xl p-4 flex justify-between items-center border border-slate-100">
              <span className="text-sm font-bold text-slate-500">Total Rooms Capacity</span>
              <span className="text-lg font-black text-slate-800">{branch.rooms}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Add Branch Modal (Mock) */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden border border-slate-100">
            <div className="p-6 border-b border-slate-100 bg-slate-50">
              <h2 className="text-xl font-bold text-slate-800">Add New Branch</h2>
              <p className="text-sm text-slate-500 font-medium mt-1">Enter the details for the new hotel location.</p>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-1">Branch Name</label>
                <input type="text" className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all font-medium text-slate-800" placeholder="e.g. Negombo Beach Resort" />
              </div>
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-1">Location / Address</label>
                <input type="text" className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all font-medium text-slate-800" placeholder="e.g. 123 Beach Road, Negombo" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-1">Phone Number</label>
                  <input type="text" className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all font-medium text-slate-800" placeholder="+94 XX XXX XXXX" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-1">Email Address</label>
                  <input type="email" className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-sky-500 focus:border-sky-500 outline-none transition-all font-medium text-slate-800" placeholder="branch@skynest.com" />
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-slate-100 flex justify-end gap-3 bg-slate-50">
              <button 
                onClick={() => setShowAddModal(false)}
                className="px-5 py-2.5 text-slate-600 font-bold hover:bg-slate-200 rounded-xl transition-colors text-sm"
              >
                Cancel
              </button>
              <button 
                onClick={() => setShowAddModal(false)}
                className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl shadow-md transition-colors text-sm"
              >
                Save Branch
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
