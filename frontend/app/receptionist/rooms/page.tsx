'use client';

import { useState } from 'react';
import { HiOutlineSearch, HiCheckCircle, HiXCircle, HiOutlineClock } from 'react-icons/hi';

// Mock data for rooms grid
const MOCK_ROOMS = Array.from({ length: 24 }, (_, i) => {
  const roomNumber = `${Math.floor(i / 8) + 1}0${(i % 8) + 1}`;
  const isSuite = i % 5 === 0;
  const rand = Math.random();
  const status = rand > 0.6 ? 'OCCUPIED' : rand > 0.4 ? 'MAINTENANCE' : 'AVAILABLE';
  
  return {
    roomNumber,
    type: isSuite ? 'Deluxe Suite' : 'Standard Room',
    status,
    price: isSuite ? 25000 : 15000
  };
});

export default function RoomAvailabilityPage() {
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  const filteredRooms = MOCK_ROOMS.filter(room => {
    if (filter !== 'ALL' && room.status !== filter) return false;
    if (search && !room.roomNumber.includes(search)) return false;
    return true;
  });

  const handleWalkInBooking = (roomNumber: string) => {
    alert(`Initiating walk-in booking flow for Room ${roomNumber}. This would open the booking form in real implementation.`);
  };

  return (
    <div className="animate-slide-up">
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-skynest-navy">Room Availability Grid</h1>
          <p className="text-sm text-gray-500 mt-1">Live overview of all hotel rooms. Click an available room to start a walk-in booking.</p>
        </div>
        
        <div className="flex gap-3">
          <select 
            className="px-4 py-3 bg-white shadow-sm border border-gray-100 rounded-xl text-sm font-black tracking-widest uppercase text-skynest-navy focus:outline-none focus:border-skynest-blue"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="ALL">All Rooms</option>
            <option value="AVAILABLE">Available</option>
            <option value="OCCUPIED">Occupied</option>
            <option value="MAINTENANCE">Maintenance</option>
          </select>
          
          <div className="relative">
            <HiOutlineSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input 
              type="text" 
              placeholder="SEARCH ROOM"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-12 pr-4 py-3 bg-white shadow-sm border border-gray-100 rounded-xl text-sm font-black tracking-widest uppercase text-skynest-navy focus:outline-none focus:border-skynest-blue w-56 placeholder:text-gray-300"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {filteredRooms.map(room => {
          const isAvailable = room.status === 'AVAILABLE';
          const isOccupied = room.status === 'OCCUPIED';
          const isMaintenance = room.status === 'MAINTENANCE';

          return (
            <div 
              key={room.roomNumber}
              onClick={() => isAvailable && handleWalkInBooking(room.roomNumber)}
              className={`relative overflow-hidden p-5 rounded-3xl flex flex-col items-center justify-center text-center transition-all duration-300 ${
                isAvailable 
                  ? 'bg-gradient-to-br from-green-400 to-green-500 shadow-xl shadow-green-500/30 hover:scale-105 cursor-pointer text-white' 
                  : isOccupied
                  ? 'bg-skynest-navy shadow-lg text-white'
                  : 'bg-gray-100 border border-gray-200 text-gray-400'
              }`}
            >
              <h3 className="text-3xl font-black mb-1">{room.roomNumber}</h3>
              <p className={`text-[9px] font-black tracking-widest uppercase mb-4 ${isAvailable ? 'text-green-100' : isOccupied ? 'text-gray-400' : 'text-gray-400'}`}>
                {room.type}
              </p>
              
              <div className={`px-4 py-1.5 rounded-full text-[10px] font-black tracking-widest uppercase flex items-center gap-1.5 shadow-inner ${
                isAvailable ? 'bg-white text-green-600' : 
                isOccupied ? 'bg-white/10 text-white' : 
                'bg-white text-gray-500'
              }`}>
                {isAvailable && <HiCheckCircle />}
                {isOccupied && <HiXCircle />}
                {isMaintenance && <HiOutlineClock />}
                {room.status}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
