'use client';

import { useState, useEffect } from 'react';
import { HiOutlinePlus, HiOutlineFilter, HiOutlineOfficeBuilding } from 'react-icons/hi';
import { getAllRooms, getBranches, getRoomTypes, createRoom } from '@/lib/api';
import type { AdminRoom, BranchItem } from '@/lib/types';

type ActiveTab = 'rooms' | 'types';
type RoomStatus = 'Active' | string;

interface RoomTypeOption {
  room_type_id: string;
  daily_rate: number;
  capacity: number;
}

interface RoomRow {
  id: number;
  type: string;
  branch: string;
  price: string;
  status: RoomStatus;
}

const ROOM_TYPE_META: Record<string, { name: string; occupancy: number }> = {
  STANDARD: { name: 'Standard Room', occupancy: 2 },
  DELUXE: { name: 'Deluxe Room', occupancy: 2 },
  FAMILY: { name: 'Family Room', occupancy: 4 },
  SUITE: { name: 'Executive Suite', occupancy: 2 },
};

export default function AdminRoomsPage() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('rooms');
  const [filterBranch, setFilterBranch] = useState<string>('All Branches');
  const [showAddRoomModal, setShowAddRoomModal] = useState<boolean>(false);
  const [showAddTypeModal, setShowAddTypeModal] = useState<boolean>(false);

  const [rooms, setRooms] = useState<RoomRow[]>([]);
  const [branches, setBranches] = useState<BranchItem[]>([]);
  const [roomTypesList, setRoomTypesList] = useState<RoomTypeOption[]>([]);

  useEffect(() => {
    Promise.all([getAllRooms(), getBranches(), getRoomTypes()]).then(([roomsData, branchesData, typesData]) => {
      setBranches(branchesData);
      setRoomTypesList(typesData);

      const branchMap = new Map(branchesData.map((b: BranchItem) => [b.branch_id, b.branch_name]));

      const formattedRooms = roomsData.map(r => ({
        id: r.room_number,
        type: r.room_type || 'Standard',
        branch: branchMap.get(r.branch_id) || `Branch ${r.branch_id}`,
        price: `LKR ${Number(r.daily_rate || 0).toLocaleString()}`,
        status: r.room_status === 'AVAILABLE' ? 'Active' : r.room_status
      }));
      setRooms(formattedRooms);
    });
  }, []);

  const [roomTypes, setRoomTypes] = useState<RoomTypeOption[]>([]);
  const [roomNumber, setRoomNumber] = useState('');
  const [branchId, setBranchId] = useState('');
  const [roomTypeId, setRoomTypeId] = useState('');
  const [capacity, setCapacity] = useState('2');
  const [saving, setSaving] = useState(false);
  const [roomError, setRoomError] = useState('');

  async function openAddRoom() {
    setRoomError('');
    setRoomNumber('');
    setCapacity('2');
    setRoomTypes([]);
    setShowAddRoomModal(true);
    try {
      const types = await getRoomTypes();
      setRoomTypes(types);
      setRoomTypeId(types[0]?.room_type_id ?? '');
      setCapacity(String(types[0]?.capacity ?? 2));
      const selected = branches.find(b => b.branch_name === filterBranch);
      setBranchId(String(selected?.branch_id ?? branches[0]?.branch_id ?? ''));
    } catch (error) {
      setRoomError(error instanceof Error ? error.message : 'Could not load room types');
    }
  }

  async function saveRoom() {
    setRoomError('');
    const number = Number(roomNumber);
    const guests = Number(capacity);
    if (!Number.isInteger(number) || number < 1 || number > 32767 ||
        !Number.isInteger(guests) || guests < 1 || guests > 32767 ||
        !branchId || !roomTypeId) {
      setRoomError('Enter valid room details and select a branch and room type.');
      return;
    }
    setSaving(true);
    try {
      await createRoom({
        room_number: number, branch_id: Number(branchId),
        room_type_id: roomTypeId, capacity: guests,
      });
    } catch (error) {
      setRoomError(error instanceof Error ? error.message : 'Could not save room');
      setSaving(false);
      return;
    }
    setShowAddRoomModal(false);
    setSaving(false);
    setFilterBranch('All Branches');
    try {
      const data = await getAllRooms();
      const branchMap = new Map(branches.map(b => [b.branch_id, b.branch_name]));
      setRooms(data.map(r => ({
        id: r.room_number,
        type: r.room_type || 'Standard',
        branch: branchMap.get(r.branch_id) || `Branch ${r.branch_id}`,
        price: `LKR ${Number(r.daily_rate ?? 0).toLocaleString()}`,
        status: r.room_status === 'AVAILABLE' ? 'Active' : r.room_status,
      })));
    } catch {
      alert('Room saved. Reload the page to refresh the list.');
    }
  }
  const filteredRooms = filterBranch === 'All Branches'
    ? rooms
    : rooms.filter(room => room.branch === filterBranch);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Room Management</h1>
          <p className="text-sm text-slate-600 mt-1 font-medium">Manage hotel rooms, room types, and pricing configurations.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="bg-white/50 backdrop-blur-md p-1 rounded-xl border border-white/40 shadow-sm flex">
            <button
              onClick={() => setActiveTab('rooms')}
              className={`px-4 py-2 text-sm font-bold rounded-lg transition-all ${activeTab === 'rooms' ? 'bg-white text-sky-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
            >
              All Rooms
            </button>
            <button
              onClick={() => setActiveTab('types')}
              className={`px-4 py-2 text-sm font-bold rounded-lg transition-all ${activeTab === 'types' ? 'bg-white text-sky-600 shadow-sm' : 'text-slate-500 hover:text-slate-800'}`}
            >
              Room Types & Pricing
            </button>
          </div>
          <button
            onClick={() => activeTab === 'rooms' ? void openAddRoom() : setShowAddTypeModal(true)}
            className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-bold rounded-xl shadow-lg transition-colors"
          >
            <HiOutlinePlus size={20} />
            {activeTab === 'rooms' ? 'Add Room' : 'Add Room Type'}
          </button>
        </div>
      </div>

      {activeTab === 'rooms' && (
        <div className="bg-white/80 backdrop-blur-md border border-white/40 shadow-xl shadow-slate-200/50 rounded-2xl overflow-hidden">
          {/* Filters */}
          <div className="p-4 border-b border-slate-200 flex gap-4 bg-slate-50/50">
            <div className="flex-1 relative">
              <HiOutlineFilter className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
              <input type="text" placeholder="Filter by room number or type..." className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-sky-500 outline-none" />
            </div>
            <select
              value={filterBranch}
              onChange={(e) => setFilterBranch(e.target.value)}
              className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 outline-none"
            >
              <option value="All Branches">All Branches</option>
              {Array.from(new Set(rooms.map(r => r.branch))).map(branch => (
                <option key={branch as string} value={branch as string}>{branch as string}</option>
              ))}
            </select>
          </div>

          {/* Table */}
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-100/50 text-slate-500 text-xs uppercase tracking-wider">
                <th className="p-4 font-bold">Room No.</th>
                <th className="p-4 font-bold">Room Type</th>
                <th className="p-4 font-bold">Branch</th>
                <th className="p-4 font-bold">Base Price</th>
                <th className="p-4 font-bold">Status</th>
                <th className="p-4 font-bold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredRooms.map((room, i) => (
                <tr key={i} className="hover:bg-slate-50/50 transition-colors">
                  <td className="p-4 font-black text-slate-800">{room.id}</td>
                  <td className="p-4 font-bold text-slate-700">{room.type}</td>
                  <td className="p-4">
                    <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
                      <HiOutlineOfficeBuilding className="text-slate-400" />
                      {room.branch}
                    </div>
                  </td>
                  <td className="p-4 font-bold text-sky-600">{room.price}<span className="text-xs text-slate-400 font-normal">/night</span></td>
                  <td className="p-4">
                    <span className={`px-2.5 py-1 rounded-md text-xs font-bold ${room.status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'}`}>
                      {room.status}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <button className="text-sky-600 font-bold text-sm hover:underline">Edit</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'types' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {roomTypesList.map((type) => {
            const meta = ROOM_TYPE_META[type.room_type_id] || {
              name: type.room_type_id,
              occupancy: type.capacity,
            };
            return (
              <div key={type.room_type_id} className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/40 shadow-xl shadow-slate-200/50 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-slate-800">{meta.name}</h3>
                    <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                      {type.room_type_id}
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 mt-1 font-medium">Max Occupancy: {type.capacity} Guests</p>
                </div>

                <div className="mt-6 pt-6 border-t border-slate-200">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Base Price</p>
                  <p className="text-2xl font-black text-slate-900">
                    LKR {Number(type.daily_rate).toLocaleString()}
                    <span className="text-xs font-semibold text-slate-400">/night</span>
                  </p>
                </div>

                <button className="w-full mt-6 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-sm transition-colors">
                  Edit Pricing & Features
                </button>
              </div>
            );
          })}
        </div>
      )}


      {/* Add Room Modal */}
      {showAddRoomModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={() => setShowAddRoomModal(false)}></div>
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6 border-b border-slate-100">
              <h3 className="text-xl font-bold text-slate-800">Add New Room</h3>
              <p className="text-sm text-slate-500 mt-1">Create a new room in a specific branch.</p>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Room Number</label>
                <input type="number" min={1} max={32767} value={roomNumber} onChange={e => setRoomNumber(e.target.value)} placeholder="e.g. 501" className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition-all text-sm font-medium" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Room Type</label>
                  <select value={roomTypeId} onChange={e => { setRoomTypeId(e.target.value); setCapacity(String(roomTypes.find(t => t.room_type_id === e.target.value)?.capacity ?? 2)); }} className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition-all text-sm font-medium text-slate-700">{roomTypes.map(t => <option key={t.room_type_id} value={t.room_type_id}>{t.room_type_id}</option>)}</select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Branch</label>
                  <select value={branchId} onChange={e => setBranchId(e.target.value)} className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition-all text-sm font-medium text-slate-700">{branches.map(b => <option key={b.branch_id} value={b.branch_id}>{b.branch_name}</option>)}</select>
                </div>
              </div>
            </div>
            <div className="px-6 pb-6 space-y-2">
  <label htmlFor="room-capacity" className="block text-sm font-bold text-slate-700">Capacity</label>
  <input id="room-capacity" type="number" min={1} max={32767}
    value={capacity} readOnly
    className="w-full px-4 py-2.5 rounded-xl border border-slate-200" />
  {roomError && <p role="alert" className="text-sm text-red-600">{roomError}</p>}
</div>
<div className="p-6 border-t border-slate-100 bg-slate-50/50 flex justify-end gap-3">
              <button onClick={() => setShowAddRoomModal(false)} className="px-5 py-2.5 text-sm font-bold text-slate-600 hover:bg-slate-200 rounded-xl transition-colors">
                Cancel
              </button>

<button onClick={() => void saveRoom()}
  disabled={saving || !roomTypes.length || !branches.length}
  className="px-5 py-2.5 text-sm font-bold text-white bg-slate-900 rounded-xl disabled:opacity-50">
  {saving ? 'Saving...' : 'Save Room'}
</button>
            </div>
          </div>
        </div>
      )}

      {/* Add Room Type Modal */}
      {showAddTypeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={() => setShowAddTypeModal(false)}></div>
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-6 border-b border-slate-100">
              <h3 className="text-xl font-bold text-slate-800">Add Room Type</h3>
              <p className="text-sm text-slate-500 mt-1">Configure a new room category and pricing.</p>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Type Name</label>
                <input type="text" placeholder="e.g. Family Suite" className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition-all text-sm font-medium" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Max Occupancy</label>
                  <input type="number" placeholder="2" className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition-all text-sm font-medium" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Base Price (LKR)</label>
                  <input type="text" placeholder="15000" className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition-all text-sm font-medium" />
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-slate-100 bg-slate-50/50 flex justify-end gap-3">
              <button onClick={() => setShowAddTypeModal(false)} className="px-5 py-2.5 text-sm font-bold text-slate-600 hover:bg-slate-200 rounded-xl transition-colors">
                Cancel
              </button>
              <button onClick={() => setShowAddTypeModal(false)} className="px-5 py-2.5 text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 rounded-xl shadow-md transition-colors">
                Save Type
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
