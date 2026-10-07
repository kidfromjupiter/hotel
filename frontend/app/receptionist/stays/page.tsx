'use client';

import { useState, useEffect } from 'react';
import { HiOutlineUserGroup, HiOutlinePlusCircle, HiOutlineCash, HiOutlineCalendar, HiX } from 'react-icons/hi';
import { getAllBookings, getBill, checkInGuest, checkOutGuest, cancelBooking, addServiceToBooking, addAmenityToBooking, extendStay, getAmenities, getServices } from '@/lib/api';
import type { StaffBooking, InvoiceSummary, ServiceCatalogueItem } from '@/lib/types';


export default function ActiveStaysPage() {
  const [selectedStay, setSelectedStay] = useState<StaffBooking | null>(null);
  const [activeStays, setActiveStays] = useState<StaffBooking[]>([]);
  const [amenities, setAmenities] = useState<Array<{ id: number; name: string; price: number }>>([]);
  const [services, setServices] = useState<Array<{ id: number; name: string; price: number }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [invoice, setInvoice] = useState<InvoiceSummary | null>(null);
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [newCheckOut, setNewCheckOut] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [bookingsData, amenitiesData, servicesData] = await Promise.all([
          getAllBookings(),
          getAmenities(),
          getServices()
        ]);
        
        // Backend returns all bookings, we only want those Checked-In for this specific view
        const checkedIn = bookingsData.filter(booking => booking.status === 'Checked-In');
        setActiveStays(checkedIn);
        setAmenities(amenitiesData);
        setServices(servicesData);
      } catch (error) {
        console.error("Failed to fetch data:", error);
        // Fallback to empty array if backend is down
        setActiveStays([]); 
        setAmenities([]);
        setServices([]);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);
  
  // Modals state
  const [activeModal, setActiveModal] = useState<'NONE' | 'AMENITIES' | 'SERVICES' | 'EXTEND' | 'BILLING'>('NONE');

  const handleOpenBilling = async () => {
    if (!selectedStay) return;
    setActiveModal('BILLING');
    setInvoice(null); // Show loading
    try {
      const billData = await getBill(selectedStay.bookingId);
      setInvoice(billData);
    } catch (error) {
      console.error("Failed to fetch bill", error);
      alert("Could not fetch bill details from the server.");
    }
  };

  const handleCheckout = async () => {
    if (!selectedStay || !invoice) return;
    setIsCheckingOut(true);
    try {
      const result = await checkOutGuest(selectedStay.bookingId);
      if (result.success) {
        alert('Checkout successful!\nDatabase updated:\n- booking.booking_status = CHECKED_OUT\n- room_details.room_status = AVAILABLE\n- billing_summary created.');
        setActiveModal('NONE');
        // Remove from list
        setActiveStays(prev => prev.filter(b => b.bookingId !== selectedStay.bookingId));
        setSelectedStay(null);
      } else {
        alert(`Checkout blocked: ${result.message}`);
      }
    } catch (err) {
      alert('Checkout failed! Database rejected the transaction (Does the guest still owe money?).');
    } finally {
      setIsCheckingOut(false);
    }
  };

  const handleAddAmenity = async (amenity: { id: number; name: string; price: number }) => {
    if (!selectedStay) return;
    try {
      const result = await addAmenityToBooking(selectedStay.bookingId, amenity.id);
      if (result.success) {
        alert(`Successfully added ${amenity.name} to guest's tab!`);
        setActiveModal('NONE');
      } else {
        alert(`Failed: ${result.message}`);
      }
    } catch (err) {
      alert('Error connecting to the database to add amenity.');
    }
  };

  const handleAddService = async (service: { id: number; name: string; price: number }) => {
    if (!selectedStay) return;
    try {
      const result = await addServiceToBooking(selectedStay.bookingId, service.name, service.price, 1);
      if (result.success) {
        // alert(`Successfully added ${service.name} to guest's tab!`);
        setActiveModal('NONE');
      } else {
        console.error(`Failed: ${result.message}`);
      }
    } catch (err) {
      console.error('Error connecting to the database to add service.');
    }
  };

  const handleExtendStay = async () => {
    if (!selectedStay || !newCheckOut) return;
    try {
      const result = await extendStay(selectedStay.bookingId, newCheckOut);
      if (result.success) {
        // alert(`Room is available!\nBooking ${selectedStay.bookingReference} end_date extended to ${newCheckOut}.`);
        setActiveModal('NONE');
        
        // Update the stay in UI to reflect new date without full refresh
        setSelectedStay({ ...selectedStay, checkOut: newCheckOut });
        setActiveStays(prev => prev.map(s => s.bookingId === selectedStay.bookingId ? { ...s, checkOut: newCheckOut } : s));
        setNewCheckOut('');
      } else {
        console.error(`Failed to extend stay: ${result.message}`);
      }
    } catch (err) {
      console.error('Error connecting to the database to extend stay.');
    }
  };

  return (
    <div className="animate-slide-up relative">
      <div className="mb-8 bg-white p-6 rounded-2xl border-2 border-slate-200 shadow-md">
        <h1 className="text-xl font-bold text-skynest-navy">Active Stays & Checkout</h1>
        <p className="text-sm text-gray-600 mt-1">Manage currently checked-in guests, add services, and process checkouts.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Active Stays List */}
        <div className="lg:col-span-1 space-y-4 flex flex-col items-start">
          <div className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-blue-100 via-white to-sky-100 border border-white shadow-md shadow-blue-900/10">
            <h2 className="text-xs font-black tracking-widest text-black uppercase">Currently Checked-In</h2>
          </div>
          {isLoading ? (
            <div className="p-5 rounded-2xl text-center bg-gradient-to-r from-white via-blue-50 to-white border border-white shadow-md shadow-blue-900/10 w-full">
              <span className="text-black font-bold">Loading active stays...</span>
            </div>
          ) : activeStays.length === 0 ? (
            <div className="p-5 rounded-2xl text-center bg-gradient-to-r from-white via-blue-50 to-white border border-white shadow-md shadow-blue-900/10 w-full">
              <span className="text-black font-bold">No active stays right now.</span>
            </div>
          ) : (
            activeStays.map(stay => (
              <div 
                key={stay.bookingId}
                onClick={() => setSelectedStay(stay)}
                className={`p-5 rounded-2xl border-2 cursor-pointer transition-all duration-300 ${
                  selectedStay?.bookingId === stay.bookingId 
                    ? 'bg-skynest-navy border-skynest-blue text-white shadow-xl scale-105' 
                    : 'bg-white border-slate-200 hover:border-skynest-blue text-skynest-navy shadow-sm hover:shadow-md'
                }`}
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="font-bold text-lg">{stay.roomNumber}</span>
                  <span className={`text-[10px] px-2 py-1 rounded-full font-bold tracking-widest ${selectedStay?.bookingId === stay.bookingId ? 'bg-skynest-blue text-white' : 'bg-green-100 text-green-700'}`}>
                    ACTIVE
                  </span>
                </div>
                <p className={`text-sm font-semibold ${selectedStay?.bookingId === stay.bookingId ? 'text-white' : 'text-gray-800'}`}>{stay.guestName}</p>
                <p className={`text-xs mt-1 font-medium ${selectedStay?.bookingId === stay.bookingId ? 'text-skynest-blue-light' : 'text-gray-500'}`}>
                  Booking: {stay.bookingId} • Out: {stay.checkOut}
                </p>
              </div>
            ))
          )}
        </div>

        {/* Stay Management Panel */}
        <div className="lg:col-span-2">
          {selectedStay ? (
            <div className="bg-white rounded-3xl shadow-xl border-2 border-slate-200 overflow-hidden animate-slide-up">
              <div className="bg-gradient-to-r from-skynest-blue to-cyan-500 p-8">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-white font-bold text-2xl">{selectedStay.guestName}</h2>
                    <p className="text-white/90 font-medium mt-1 tracking-wider uppercase text-xs">Room {selectedStay.roomNumber}</p>
                  </div>
                  <div className="bg-white/20 backdrop-blur-md px-4 py-2 rounded-xl text-white text-center border border-white/30">
                    <p className="text-[9px] font-semibold tracking-widest uppercase opacity-90">Check-out</p>
                    <p className="font-bold">{selectedStay.checkOut}</p>
                  </div>
                </div>
              </div>

              <div className="p-8 space-y-8">
                {/* Action Buttons */}
                <div>
                  <h3 className="text-xs font-semibold text-gray-500 tracking-widest uppercase mb-4">Add to Tab</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <button onClick={() => setActiveModal('SERVICES')} className="py-6 bg-slate-50 border-2 border-slate-200 shadow-sm rounded-2xl font-semibold text-sm text-skynest-navy hover:bg-skynest-blue hover:text-white hover:border-skynest-blue transition-all flex flex-col items-center justify-center gap-2 group">
                      <HiOutlinePlusCircle size={24} className="text-skynest-blue group-hover:text-white transition-colors" /> 
                      Services
                    </button>
                    <button onClick={() => setActiveModal('AMENITIES')} className="py-6 bg-slate-50 border-2 border-slate-200 shadow-sm rounded-2xl font-semibold text-sm text-skynest-navy hover:bg-skynest-blue hover:text-white hover:border-skynest-blue transition-all flex flex-col items-center justify-center gap-2 group">
                      <HiOutlinePlusCircle size={24} className="text-skynest-blue group-hover:text-white transition-colors" /> 
                      Amenities
                    </button>
                    <button onClick={() => setActiveModal('EXTEND')} className="py-6 bg-slate-50 border-2 border-slate-200 shadow-sm rounded-2xl font-semibold text-sm text-skynest-navy hover:bg-skynest-blue hover:text-white hover:border-skynest-blue transition-all flex flex-col items-center justify-center gap-2 group">
                      <HiOutlineCalendar size={24} className="text-skynest-blue group-hover:text-white transition-colors" /> 
                      Extend Stay
                    </button>
                  </div>
                </div>

                {/* Checkout & Billing */}
                <div className="pt-6 border-t border-gray-200">
                  <h3 className="text-xs font-semibold text-gray-500 tracking-widest uppercase mb-4">Finalize</h3>
                  <button onClick={handleOpenBilling} className="w-full py-4 bg-skynest-navy text-white font-bold rounded-xl hover:bg-skynest-blue transition-colors shadow-lg shadow-skynest-navy/20 tracking-wide uppercase text-sm flex items-center justify-center gap-2">
                    <HiOutlineCash size={20} /> Generate Bill & Check-Out
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full bg-white border-2 border-slate-200 rounded-3xl flex flex-col items-center justify-center text-gray-500 p-12 min-h-[400px] shadow-md">
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
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-skynest-navy/50 backdrop-blur-sm p-4 animate-fade-in"
          onClick={() => setActiveModal('NONE')}
        >
          <div 
            className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            
            <div className="flex justify-between items-center p-6 border-b border-gray-100 bg-gray-50">
              <h2 className="font-black text-xl text-skynest-navy">
                {activeModal === 'AMENITIES' && 'Add Extra Amenity'}
                {activeModal === 'SERVICES' && 'Add Room Service'}
                {activeModal === 'EXTEND' && 'Extend Stay'}
                {activeModal === 'BILLING' && 'Final Billing Summary'}
              </h2>
              <button 
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setActiveModal('NONE');
                  setNewCheckOut('');
                }} 
                className="text-gray-400 hover:text-skynest-navy bg-white p-2 rounded-full shadow-sm relative z-50 cursor-pointer"
              >
                <HiX size={20} className="pointer-events-none" />
              </button>
            </div>

            <div className="p-6">
              
              {/* Amenities Modal Content */}
              {activeModal === 'AMENITIES' && (
                <div className="space-y-3">
                  <p className="text-sm text-gray-500 mb-4">Select an amenity to add to the guest's tab (updates <code className="text-xs bg-gray-100 px-1 rounded">booking_extra_amenities</code>).</p>
                  {amenities.map(a => (
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
                  {services.map(s => (
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
                    <input 
                      type="date" 
                      value={newCheckOut}
                      onChange={(e) => setNewCheckOut(e.target.value)}
                      min={selectedStay?.checkOut} 
                      className="w-full p-4 border-2 border-gray-200 rounded-xl text-skynest-navy font-bold focus:outline-none focus:border-skynest-blue" 
                    />
                  </div>
                  <button 
                    type="button"
                    onClick={(e) => {
                      e.preventDefault();
                      handleExtendStay();
                    }} 
                    disabled={!newCheckOut} 
                    className="w-full py-4 bg-skynest-blue text-white font-black rounded-xl hover:bg-blue-600 transition-colors disabled:opacity-50"
                  >
                    Confirm Extension
                  </button>
                </div>
              )}

              {/* Billing Summary Modal Content */}
              {activeModal === 'BILLING' && (
                <div className="space-y-6">
                  {!invoice ? (
                    <div className="p-8 text-center text-gray-500 font-bold animate-pulse">Calculating final bill...</div>
                  ) : (
                    <>
                      <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 space-y-2 text-sm">
                        <div className="flex justify-between"><span className="text-gray-500">Room Charges</span><span className="font-bold">LKR {invoice.totalRoomCharges.toLocaleString()}</span></div>
                        <div className="flex justify-between"><span className="text-gray-500">Extra Amenities</span><span className="font-bold">LKR {invoice.totalAmenityCharges.toLocaleString()}</span></div>
                        <div className="flex justify-between"><span className="text-gray-500">Room Services</span><span className="font-bold">LKR {invoice.totalServiceCharges.toLocaleString()}</span></div>
                        <div className="flex justify-between"><span className="text-gray-500">Taxes</span><span className="font-bold">LKR {invoice.totalTaxAmount.toLocaleString()}</span></div>
                        
                        <hr className="my-2 border-gray-200" />
                        
                        <div className="flex justify-between text-lg"><span className="font-black text-skynest-navy">Grand Total</span><span className="font-black text-skynest-blue">LKR {invoice.grandTotal.toLocaleString()}</span></div>
                        
                        <div className="flex justify-between text-green-600"><span className="font-bold">Amount Paid</span><span className="font-bold">LKR {invoice.amountPaid.toLocaleString()}</span></div>
                        
                        <hr className="my-2 border-gray-200" />
                        <div className="flex justify-between text-red-500 text-lg"><span className="font-black">Balance Due</span><span className="font-black">LKR {(invoice.grandTotal - invoice.amountPaid).toLocaleString()}</span></div>
                      </div>

                      <div>
                        <label className="block text-xs font-bold text-gray-500 mb-2">Payment Method</label>
                        <select className="w-full p-3 border-2 border-gray-200 rounded-xl font-bold text-skynest-navy focus:outline-none focus:border-skynest-blue">
                          <option>Credit Card</option>
                          <option>Cash</option>
                        </select>
                      </div>

                      <button 
                        onClick={handleCheckout} 
                        disabled={isCheckingOut}
                        className="w-full py-4 bg-green-500 text-white font-black uppercase tracking-widest rounded-xl hover:bg-green-600 transition-colors shadow-lg shadow-green-500/30 disabled:opacity-50"
                      >
                        {isCheckingOut ? 'Processing...' : 'Complete Checkout'}
                      </button>
                    </>
                  )}
                </div>
              )}

            </div>
          </div>
        </div>
      )}

    </div>
  );
}
