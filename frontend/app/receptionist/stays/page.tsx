'use client';

import { useState } from 'react';
import { HiOutlineUserGroup, HiOutlinePlusCircle, HiOutlineCash, HiOutlineCalendar, HiX } from 'react-icons/hi';

const MOCK_STAYS = [
  { id: 'BKG-9921', guest: 'Kasun Perera', room: '201', checkIn: '2026-09-24', checkOut: '2026-09-26', status: 'CHECKED_IN' },
  { id: 'BKG-9922', guest: 'Amal Silva', room: '305', checkIn: '2026-09-23', checkOut: '2026-09-25', status: 'CHECKED_IN' },
];

const MOCK_AMENITIES = [
  { id: 1, name: 'Extra Towels', price: 500 },
  { id: 2, name: 'Mini Bar Restock', price: 3500 },
  { id: 3, name: 'Late Checkout', price: 5000 },
];

const MOCK_SERVICES = [
  { id: 101, name: 'Spa Session', price: 12000 },
  { id: 102, name: 'Airport Transfer', price: 8000 },
  { id: 103, name: 'In-room Dining', price: 4500 },
];

export default function ActiveStaysPage() {
  const [selectedStay, setSelectedStay] = useState<any | null>(null);
  
  // Modals state
  const [activeModal, setActiveModal] = useState<'NONE' | 'AMENITIES' | 'SERVICES' | 'EXTEND' | 'BILLING'>('NONE');

  const handleCheckout = () => {
    alert('Checkout successful!\nDatabase updated:\n- booking.booking_status = CHECKED_OUT\n- room_details.room_status = AVAILABLE\n- billing_summary created.');
    setActiveModal('NONE');
    setSelectedStay(null);
  };

  const handleAddAmenity = (amenity: any) => {
    alert(`Inserted ${amenity.name} into booking_extra_amenities for booking ${selectedStay.id}`);
    setActiveModal('NONE');
  };

  const handleAddService = (service: any) => {
    alert(`Inserted ${service.name} into service_charges for booking ${selectedStay.id}`);
    setActiveModal('NONE');
  };

  const handleExtendStay = () => {
    alert(`Queried room_details. Room is available!\nBooking ${selectedStay.id} end_date extended.`);
    setActiveModal('NONE');
  };

  return (
    <div className="animate-slide-up relative">
      <div className="mb-8">
        <h1 className="text-2xl font-black text-skynest-navy">Active Stays & Checkout</h1>
        <p className="text-sm text-gray-500 mt-1">Manage currently checked-in guests, add services, and process checkouts.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Active Stays List */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-sm font-bold tracking-widest text-gray-400 uppercase">Currently Checked-In</h2>
          {MOCK_STAYS.map(stay => (
            <div 
              key={stay.id}
              onClick={() => setSelectedStay(stay)}
              className={`p-5 rounded-2xl border cursor-pointer transition-all duration-300 ${
                selectedStay?.id === stay.id 
                  ? 'bg-skynest-navy border-skynest-navy text-white shadow-xl scale-105' 
                  : 'bg-white border-gray-200 hover:border-skynest-blue/50 text-skynest-navy'
              }`}
            >
              <div className="flex justify-between items-center mb-2">
                <span className="font-black text-xl">{stay.room}</span>
                <span className={`text-[10px] px-2 py-1 rounded-full font-black tracking-widest ${selectedStay?.id === stay.id ? 'bg-skynest-blue text-white' : 'bg-green-100 text-green-700'}`}>
                  ACTIVE
                </span>
              </div>
              <p className={`text-base font-bold ${selectedStay?.id === stay.id ? 'text-white' : 'text-gray-800'}`}>{stay.guest}</p>
              <p className={`text-xs mt-1 font-semibold ${selectedStay?.id === stay.id ? 'text-skynest-blue-light' : 'text-gray-400'}`}>
                Booking: {stay.id} • Out: {stay.checkOut}
              </p>
            </div>
          ))}
        </div>

        {/* Stay Management Panel */}
        <div className="lg:col-span-2">
          {selectedStay ? (
            <div className="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden animate-slide-up">
              <div className="bg-skynest-blue p-8">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-white font-black text-3xl">{selectedStay.guest}</h2>
                    <p className="text-white/80 font-bold mt-1 tracking-wider uppercase text-sm">Room {selectedStay.room}</p>
                  </div>
                  <div className="bg-white/20 backdrop-blur-md px-4 py-2 rounded-xl text-white text-center">
                    <p className="text-[10px] font-bold tracking-widest uppercase opacity-80">Check-out</p>
                    <p className="font-black">{selectedStay.checkOut}</p>
                  </div>
                </div>
              </div>

              <div className="p-8 space-y-8">
                {/* Action Buttons */}
                <div>
                  <h3 className="text-xs font-black text-gray-400 tracking-widest uppercase mb-4">Add to Tab</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <button onClick={() => setActiveModal('SERVICES')} className="py-6 bg-gray-50 border-2 border-gray-100 rounded-2xl font-bold text-skynest-navy hover:bg-skynest-blue hover:text-white hover:border-skynest-blue transition-all flex flex-col items-center justify-center gap-2 group">
                      <HiOutlinePlusCircle size={28} className="text-skynest-blue group-hover:text-white transition-colors" /> 
                      Services
                    </button>
                    <button onClick={() => setActiveModal('AMENITIES')} className="py-6 bg-gray-50 border-2 border-gray-100 rounded-2xl font-bold text-skynest-navy hover:bg-skynest-blue hover:text-white hover:border-skynest-blue transition-all flex flex-col items-center justify-center gap-2 group">
                      <HiOutlinePlusCircle size={28} className="text-skynest-blue group-hover:text-white transition-colors" /> 
                      Amenities
                    </button>
                    <button onClick={() => setActiveModal('EXTEND')} className="py-6 bg-gray-50 border-2 border-gray-100 rounded-2xl font-bold text-skynest-navy hover:bg-skynest-blue hover:text-white hover:border-skynest-blue transition-all flex flex-col items-center justify-center gap-2 group">
                      <HiOutlineCalendar size={28} className="text-skynest-blue group-hover:text-white transition-colors" /> 
                      Extend Stay
                    </button>
                  </div>
                </div>

                {/* Checkout & Billing */}
                <div className="pt-6 border-t-2 border-dashed border-gray-100">
                  <h3 className="text-xs font-black text-gray-400 tracking-widest uppercase mb-4">Finalize</h3>
                  <button onClick={() => setActiveModal('BILLING')} className="w-full py-5 bg-skynest-navy text-white font-black rounded-2xl hover:bg-skynest-blue transition-colors shadow-xl shadow-skynest-navy/20 tracking-widest uppercase text-lg flex items-center justify-center gap-3">
                    <HiOutlineCash size={24} /> Generate Bill & Check-Out
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full bg-white border-2 border-dashed border-gray-200 rounded-3xl flex flex-col items-center justify-center text-gray-400 p-12 min-h-[400px]">
              <div className="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-6">
                <HiOutlineUserGroup size={48} className="opacity-50" />
              </div>
              <p className="font-bold text-lg text-skynest-navy">No Stay Selected</p>
              <p className="text-sm mt-2 text-center max-w-xs">Select a checked-in guest from the list to manage their stay, add amenities, or process checkout.</p>
            </div>
          )}
        </div>
      </div>

      {/* --- MODALS --- */}
      {activeModal !== 'NONE' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-skynest-navy/50 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-slide-up">
            
            <div className="flex justify-between items-center p-6 border-b border-gray-100 bg-gray-50">
              <h2 className="font-black text-xl text-skynest-navy">
                {activeModal === 'AMENITIES' && 'Add Extra Amenity'}
                {activeModal === 'SERVICES' && 'Add Room Service'}
                {activeModal === 'EXTEND' && 'Extend Stay'}
                {activeModal === 'BILLING' && 'Final Billing Summary'}
              </h2>
              <button onClick={() => setActiveModal('NONE')} className="text-gray-400 hover:text-skynest-navy bg-white p-2 rounded-full shadow-sm">
                <HiX size={20} />
              </button>
            </div>

            <div className="p-6">
              
              {/* Amenities Modal Content */}
              {activeModal === 'AMENITIES' && (
                <div className="space-y-3">
                  <p className="text-sm text-gray-500 mb-4">Select an amenity to add to the guest's tab (updates <code className="text-xs bg-gray-100 px-1 rounded">booking_extra_amenities</code>).</p>
                  {MOCK_AMENITIES.map(a => (
                    <button key={a.id} onClick={() => handleAddAmenity(a)} className="w-full flex justify-between items-center p-4 border-2 border-gray-100 rounded-xl hover:border-skynest-blue hover:bg-skynest-blue-pale transition-colors text-left">
                      <span className="font-bold text-skynest-navy">{a.name}</span>
                      <span className="font-black text-skynest-blue">LKR {a.price}</span>
                    </button>
                  ))}
                </div>
              )}

              {/* Services Modal Content */}
              {activeModal === 'SERVICES' && (
                <div className="space-y-3">
                  <p className="text-sm text-gray-500 mb-4">Select a service to add to the guest's tab (updates <code className="text-xs bg-gray-100 px-1 rounded">service_charges</code>).</p>
                  {MOCK_SERVICES.map(s => (
                    <button key={s.id} onClick={() => handleAddService(s)} className="w-full flex justify-between items-center p-4 border-2 border-gray-100 rounded-xl hover:border-skynest-blue hover:bg-skynest-blue-pale transition-colors text-left">
                      <span className="font-bold text-skynest-navy">{s.name}</span>
                      <span className="font-black text-skynest-blue">LKR {s.price}</span>
                    </button>
                  ))}
                </div>
              )}

              {/* Extend Stay Modal Content */}
              {activeModal === 'EXTEND' && (
                <div className="space-y-4">
                  <p className="text-sm text-gray-500">Querying room availability to ensure the room is free for the extended dates...</p>
                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-1">New Check-out Date</label>
                    <input type="date" className="w-full p-4 border-2 border-gray-200 rounded-xl text-skynest-navy font-bold focus:outline-none focus:border-skynest-blue" />
                  </div>
                  <button onClick={handleExtendStay} className="w-full py-4 bg-skynest-blue text-white font-black rounded-xl hover:bg-skynest-blue-hover transition-colors">
                    Confirm Extension
                  </button>
                </div>
              )}

              {/* Billing Summary Modal Content */}
              {activeModal === 'BILLING' && (
                <div className="space-y-6">
                  <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 space-y-2 text-sm">
                    <div className="flex justify-between"><span className="text-gray-500">Room Fee (2 Nights)</span><span className="font-bold">LKR 50,000</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">Extra Amenities</span><span className="font-bold">LKR 3,500</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">Room Services</span><span className="font-bold">LKR 12,000</span></div>
                    <div className="flex justify-between"><span className="text-gray-500">Taxes (15%)</span><span className="font-bold">LKR 9,825</span></div>
                    
                    <hr className="my-2 border-gray-200" />
                    
                    <div className="flex justify-between text-lg"><span className="font-black text-skynest-navy">Grand Total</span><span className="font-black text-skynest-blue">LKR 75,325</span></div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-gray-500 mb-2">Payment Method</label>
                    <select className="w-full p-3 border-2 border-gray-200 rounded-xl font-bold text-skynest-navy focus:outline-none focus:border-skynest-blue">
                      <option>Credit Card</option>
                      <option>Cash</option>
                    </select>
                  </div>

                  <button onClick={handleCheckout} className="w-full py-4 bg-green-500 text-white font-black uppercase tracking-widest rounded-xl hover:bg-green-600 transition-colors shadow-lg shadow-green-500/30">
                    Complete Checkout
                  </button>
                </div>
              )}

            </div>
          </div>
        </div>
      )}

    </div>
  );
}
