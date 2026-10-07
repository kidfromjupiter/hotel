'use client';

import { useState, useEffect } from 'react';
import { HiOutlineSearch, HiCheckCircle, HiXCircle, HiOutlineClock } from 'react-icons/hi';
import { getAllRooms } from '@/lib/api';
import type { HotelRoom } from '@/lib/types';

export default function RoomAvailabilityPage() {
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  const [rooms, setRooms] = useState<HotelRoom[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        const data = await getAllRooms();
        setRooms(data);
      } catch (error) {
        console.error("Failed to fetch rooms:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchRooms();
  }, []);

  const filteredRooms = rooms.filter(room => {
    if (filter !== 'ALL' && room.room_status !== filter) return false;
    if (search && !String(room.room_number).includes(search)) return false;
    return true;
  });

  const handleWalkInBooking = (roomNumber: number) => {
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

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-skynest-blue"></div>
        </div>
      ) : (
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
        {filteredRooms.map(room => {
          const isAvailable = room.room_status === 'AVAILABLE';
          const isOccupied = room.room_status === 'OCCUPIED';
          const isMaintenance = room.room_status === 'MAINTENANCE';

          return (
            <div 
              key={`${room.branch_id}-${room.room_number}`}
              onClick={() => isAvailable && handleWalkInBooking(room.room_number)}
              className={`relative overflow-hidden p-5 rounded-2xl flex flex-col items-center justify-center text-center transition-all duration-300 border-2 ${
                isAvailable 
                  ? 'bg-white border-slate-200 shadow-sm hover:shadow-lg hover:border-skynest-blue hover:-translate-y-1 cursor-pointer group' 
                  : isOccupied
                  ? 'bg-skynest-navy border-skynest-navy shadow-lg text-white'
                  : 'bg-slate-100 border-dashed border-slate-300 text-slate-400'
              }`}
            >
              {isAvailable && (
                <div className="absolute top-0 right-0 w-16 h-16 bg-skynest-blue/10 rounded-bl-full -z-10 group-hover:bg-skynest-blue/20 transition-colors" />
              )}
              
              <h3 className={`text-3xl font-bold mb-1 tracking-tight ${isAvailable ? 'text-skynest-navy' : isOccupied ? 'text-white' : 'text-gray-500'}`}>
                {room.room_number}
              </h3>
              
              <p className={`text-[10px] font-semibold tracking-widest uppercase mb-6 ${
                isAvailable ? 'text-skynest-blue' : isOccupied ? 'text-gray-300' : 'text-gray-400'
              }`}>
                {room.type_name}
              </p>
              
              <div className={`px-4 py-1.5 rounded-full text-[10px] font-bold tracking-widest uppercase flex items-center gap-1.5 ${
                isAvailable ? 'bg-skynest-blue text-white shadow-md shadow-skynest-blue/20' : 
                isOccupied ? 'bg-white/20 text-white' : 
                'bg-gray-200 text-gray-500'
              }`}>
                {isAvailable && <HiCheckCircle size={14} />}
                {isOccupied && <HiXCircle size={14} />}
                {isMaintenance && <HiOutlineClock size={14} />}
                {room.room_status}
              </div>
            </div>
          );
        })}
      </div>
      )}
    </div>
  );
}
