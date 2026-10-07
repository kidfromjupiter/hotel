'use client';

import { useState, useEffect } from 'react';
import { HiOutlineUserAdd, HiOutlineStar, HiOutlinePencilAlt, HiOutlineSearch } from 'react-icons/hi';

export default function GuestManagementPage() {
  const [activeTab, setActiveTab] = useState<'expected' | 'members'>('expected');
  const [expectedGuests, setExpectedGuests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadExpectedGuests() {
      try {
        setLoading(true);
        // Note: Using the exact backend port which should be 8000 by default, 
        // or using the lib/api.ts helper if it existed for this. We will use fetch directly.
        const res = await fetch('http://localhost:8000/api/v1/bookings/?status=Confirmed');
        if (res.ok) {
          const data = await res.json();
          setExpectedGuests(data);
        }
      } catch (err) {
        console.error("Failed to load expected guests:", err);
      } finally {
        setLoading(false);
      }
    }
    
    if (activeTab === 'expected') {
      loadExpectedGuests();
    }
  }, [activeTab]);
  
  // Handlers for mock APIs
  const handleUpdatePhone = () => {
    const newPhone = prompt("Enter new phone number:");
    if (newPhone) {
      alert(`Guest phone updated in guest table and sky-nest membership table to: ${newPhone}`);
    }
  };

  const handleCreateMembership = () => {
    alert('SkyNest Membership created successfully! (Mock API Call)');
  };

  const handleCheckPaymentStatus = () => {
    alert('Checking status of previous payment and previous booking... \nStatus: PAID IN FULL');
  };

  return (
    <div className="animate-slide-up">
      <div className="mb-8">
        <h1 className="text-2xl font-black text-skynest-navy">Guest & Membership Management</h1>
        <p className="text-sm text-gray-500 mt-1">View expected arrivals, check previous bookings/payments, and manage SkyNest memberships.</p>
      </div>

      <div className="flex gap-4 mb-6 border-b border-gray-200">
        <button 
          onClick={() => setActiveTab('expected')}
          className={`pb-3 text-sm font-bold tracking-wide uppercase transition-colors ${activeTab === 'expected' ? 'text-skynest-blue border-b-2 border-skynest-blue' : 'text-gray-400 hover:text-gray-700'}`}
        >
          Expected Arrivals
        </button>
        <button 
          onClick={() => setActiveTab('members')}
          className={`pb-3 text-sm font-bold tracking-wide uppercase transition-colors ${activeTab === 'members' ? 'text-skynest-blue border-b-2 border-skynest-blue' : 'text-gray-400 hover:text-gray-700'}`}
        >
          Membership & Profiles
        </button>
      </div>

      {activeTab === 'expected' && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
            <h3 className="font-bold text-skynest-navy">Today's Expected Guests</h3>
          </div>
          <div className="divide-y divide-gray-100">
            {loading ? (
              <div className="p-8 text-center text-gray-500 font-bold">Loading expected guests...</div>
            ) : expectedGuests.length === 0 ? (
              <div className="p-8 text-center text-gray-500 font-bold">No expected arrivals found.</div>
            ) : (
              expectedGuests.map((guest: any) => (
                <div key={guest.booking_id} className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-lg font-bold text-skynest-navy">{guest.guest_name}</h4>
                      {guest.is_member && <span className="bg-amber-100 text-amber-700 text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center gap-1"><HiOutlineStar /> MEMBER</span>}
                    </div>
                    <p className="text-sm text-gray-500">Booking Ref: {guest.booking_id} • Phone: {guest.guest_phone || 'N/A'}</p>
                  </div>
                  
                  <div className="flex gap-3">
                    <button onClick={handleCheckPaymentStatus} className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-skynest-navy text-xs font-bold rounded-lg transition-colors">
                      Check Payment Status
                    </button>
                    <button onClick={handleUpdatePhone} className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-skynest-navy text-xs font-bold rounded-lg transition-colors flex items-center gap-1">
                      <HiOutlinePencilAlt /> Edit Details
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === 'members' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-200">
            <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-xl flex items-center justify-center mb-4">
              <HiOutlineStar size={24} />
            </div>
            <h3 className="text-lg font-bold text-skynest-navy mb-2">Create SkyNest Membership</h3>
            <p className="text-sm text-gray-500 mb-6">Enroll a guest into the SkyNest membership program to apply automatic discounts to their current and future stays.</p>
            <button onClick={handleCreateMembership} className="w-full py-3 bg-skynest-navy text-white font-bold rounded-xl hover:bg-skynest-blue transition-colors flex justify-center items-center gap-2">
              <HiOutlineUserAdd size={18} /> Enroll New Member
            </button>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-200">
            <div className="w-12 h-12 bg-skynest-blue-pale text-skynest-blue rounded-xl flex items-center justify-center mb-4">
              <HiOutlineSearch size={24} />
            </div>
            <h3 className="text-lg font-bold text-skynest-navy mb-2">Search Guest Records</h3>
            <p className="text-sm text-gray-500 mb-6">Look up previous bookings, previous payments, and historical data for returning guests.</p>
            <div className="flex gap-2">
              <input type="text" placeholder="Enter Guest ID or Phone" className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-skynest-blue" />
              <button onClick={handleCheckPaymentStatus} className="px-6 py-3 bg-skynest-blue text-white font-bold rounded-xl hover:bg-skynest-blue-hover transition-colors">
                Search
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
