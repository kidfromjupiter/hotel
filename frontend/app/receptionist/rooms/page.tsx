'use client';

import { useState } from 'react';
import { HiOutlineSearch, HiCheckCircle, HiXCircle, HiOutlineClock } from 'react-icons/hi';

// Mock data for rooms grid
const MOCK_ROOMS = Array.from({ length: 24 }, (_, i) => {
  const roomNumber = `${Math.floor(i / 8) + 1}0${(i % 8) + 1}`;
  const isSuite = i % 5 === 0;
  
  // Use deterministic logic instead of Math.random() to prevent hydration errors
  let status = 'AVAILABLE';
  if (i % 3 === 1) status = 'OCCUPIED';
  else if (i % 7 === 0 && i !== 0) status = 'MAINTENANCE';
  
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
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4 bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-white/50 shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-skynest-navy">Room Availability Grid</h1>
          <p className="text-sm text-gray-500 mt-1">Live overview of all hotel rooms. Click an available room to start a walk-in booking.</p>
        </div>
        
        <div className="flex gap-3">
          <select 
            className="px-4 py-3 bg-white/80 backdrop-blur-md shadow-sm border border-white/50 rounded-xl text-sm font-bold tracking-widest uppercase text-skynest-navy focus:outline-none focus:border-skynest-blue"
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
              className="pl-12 pr-4 py-3 bg-white/80 backdrop-blur-md shadow-sm border border-white/50 rounded-xl text-sm font-bold tracking-widest uppercase text-skynest-navy focus:outline-none focus:border-skynest-blue w-56 placeholder:text-gray-400"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
        {filteredRooms.map(room => {
          const isAvailable = room.status === 'AVAILABLE';
          const isOccupied = room.status === 'OCCUPIED';
          const isMaintenance = room.status === 'MAINTENANCE';

          return (
            <div 
              key={room.roomNumber}
              onClick={() => isAvailable && handleWalkInBooking(room.roomNumber)}
              className={`relative overflow-hidden p-6 rounded-2xl flex flex-col items-center justify-center text-center transition-all duration-300 backdrop-blur-md border ${
                isAvailable 
                  ? 'bg-white/80 border-white/60 shadow-sm hover:shadow-xl hover:border-skynest-blue/50 hover:-translate-y-1 cursor-pointer group' 
                  : isOccupied
                  ? 'bg-skynest-navy/90 border-transparent shadow-lg text-white'
                  : 'bg-white/40 border-dashed border-gray-300 text-gray-500'
              }`}
            >
              {isAvailable && (
                <div className="absolute top-0 right-0 w-16 h-16 bg-skynest-blue/10 rounded-bl-full -z-10 group-hover:bg-skynest-blue/20 transition-colors" />
              )}
              
              <h3 className={`text-3xl font-bold mb-1 tracking-tight ${isAvailable ? 'text-skynest-navy' : isOccupied ? 'text-white' : 'text-gray-500'}`}>
                {room.roomNumber}
              </h3>
              
              <p className={`text-[10px] font-semibold tracking-widest uppercase mb-6 ${
                isAvailable ? 'text-skynest-blue' : isOccupied ? 'text-gray-300' : 'text-gray-400'
              }`}>
                {room.type}
              </p>
              
              <div className={`px-4 py-1.5 rounded-full text-[10px] font-bold tracking-widest uppercase flex items-center gap-1.5 ${
                isAvailable ? 'bg-skynest-blue text-white shadow-md shadow-skynest-blue/20' : 
                isOccupied ? 'bg-white/20 text-white' : 
                'bg-gray-200 text-gray-500'
              }`}>
                {isAvailable && <HiCheckCircle size={14} />}
                {isOccupied && <HiXCircle size={14} />}
                {isMaintenance && <HiOutlineClock size={14} />}
                {room.status}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
