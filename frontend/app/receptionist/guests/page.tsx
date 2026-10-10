'use client';

import { useState, useEffect } from 'react';
import { HiOutlineUserAdd, HiOutlineStar, HiOutlinePencilAlt, HiOutlineSearch, HiX, HiOutlineMail, HiOutlinePhone, HiOutlineUser } from 'react-icons/hi';
import { createMembership, getAllBookings } from '../../../lib/api';
import type { ExpectedGuest } from '../../../lib/types';

export default function GuestManagementPage() {
  const [activeTab, setActiveTab] = useState<'expected' | 'members'>('expected');
  const [isMembershipModalOpen, setIsMembershipModalOpen] = useState(false);
  const [membershipData, setMembershipData] = useState({ name: '', phone: '', email: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [paymentStatus, setPaymentStatus] = useState<'IDLE' | 'LOADING' | 'SUCCESS'>('IDLE');
  const [expectedGuests, setExpectedGuests] = useState<ExpectedGuest[]>([]);

  useEffect(() => {
    getAllBookings().then(data => {
      // Filter for expected arrivals
      const expected = data
        .filter(b => b.status === 'Confirmed')
        .map(b => ({
          id: b.bookingReference,
          guest: b.guestName,
          checkInDate: b.checkIn,
          status: 'EXPECTED',
          phone: b.phone,
          isMember: false // simplified for now
        }));
      setExpectedGuests(expected);
    });
  }, []);
  
  // Handlers for mock APIs
  const handleUpdatePhone = async (guestId: number) => {
    const newPhone = prompt("Enter new phone number:");
    if (newPhone) {
      try {
        const response = await fetch(`/api/v1/guests/${guestId}/phone`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone: newPhone })
        });
        const result = await response.json();
        if (result.success) {
          alert(`Guest phone updated successfully!`);
          // Update local state to reflect change
          setExpectedGuests(prev => prev.map(g => g.id === guestId ? { ...g, phone: newPhone } : g));
        } else {
          alert(`Failed to update phone: ${result.message}`);
        }
      } catch (error) {
        alert('Error connecting to backend to update phone.');
      }
    }
  };

  const handleCreateMembershipClick = () => {
    setIsMembershipModalOpen(true);
  };

  const submitMembership = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const result = await createMembership(membershipData);
      if (result.success) {
        alert(result.message);
        setIsMembershipModalOpen(false);
        setMembershipData({ name: '', phone: '', email: '' });
      }
    } catch (error) {
      alert('Failed to create membership');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCheckPaymentStatus = () => {
    setIsPaymentModalOpen(true);
    setPaymentStatus('LOADING');
    setTimeout(() => {
      setPaymentStatus('SUCCESS');
    }, 1500);
  };

  return (
    <div className="animate-slide-up">
      <div className="mb-8 bg-white/70 backdrop-blur-md p-6 rounded-2xl border border-white/50 shadow-sm">
        <h1 className="text-xl font-bold text-skynest-navy">Guest & Membership Management</h1>
        <p className="text-sm text-gray-500 mt-1">View expected arrivals, check previous bookings/payments, and manage SkyNest memberships.</p>
      </div>

      <div className="flex gap-2 mb-6 bg-white/60 backdrop-blur-md p-1.5 rounded-xl border border-white/50 w-fit shadow-sm">
        <button 
          onClick={() => setActiveTab('expected')}
          className={`px-6 py-2.5 text-sm font-bold tracking-wide uppercase rounded-lg transition-all ${activeTab === 'expected' ? 'bg-skynest-blue text-white shadow-md' : 'text-skynest-navy/70 hover:text-skynest-navy hover:bg-white/50'}`}
        >
          Expected Arrivals
        </button>
        <button 
          onClick={() => setActiveTab('members')}
          className={`px-6 py-2.5 text-sm font-bold tracking-wide uppercase rounded-lg transition-all ${activeTab === 'members' ? 'bg-skynest-blue text-white shadow-md' : 'text-skynest-navy/70 hover:text-skynest-navy hover:bg-white/50'}`}
        >
          Membership & Profiles
        </button>
      </div>

      {activeTab === 'expected' && (
        <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-sm border border-white/50 overflow-hidden">
          <div className="p-6 bg-white/40 border-b border-white/50 flex justify-between items-center">
            <h3 className="font-semibold text-skynest-navy">Expected Guests</h3>
          </div>
          <div className="divide-y divide-gray-100">
            {expectedGuests.map(guest => (
              <div key={guest.id} className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-lg font-semibold text-skynest-navy">{guest.guest}</h4>
                    {guest.isMember && <span className="bg-amber-100 text-amber-700 text-[10px] px-2 py-0.5 rounded-full font-bold flex items-center gap-1"><HiOutlineStar /> MEMBER</span>}
                  </div>
                  <p className="text-sm text-gray-500">Booking Ref: {guest.id} • Phone: {guest.phone} • Check-In: {guest.checkInDate}</p>
                </div>
                
                <div className="flex gap-3">
                  <button onClick={handleCheckPaymentStatus} className="px-4 py-2 bg-white hover:bg-gray-50 border border-gray-200 text-skynest-navy text-xs font-semibold rounded-lg transition-colors shadow-sm">
                    Check Payment Status
                  </button>
                  <button onClick={handleUpdatePhone} className="px-4 py-2 bg-white hover:bg-gray-50 border border-gray-200 text-skynest-navy text-xs font-semibold rounded-lg transition-colors flex items-center gap-1 shadow-sm">
                    <HiOutlinePencilAlt /> Edit Details
                  </button>
                </div>
              </div>
            ))}
            {expectedGuests.length === 0 && (
              <div className="p-6 text-center text-gray-500 text-sm">
                No expected arrivals right now.
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'members' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white/80 backdrop-blur-md p-8 rounded-2xl shadow-sm border border-white/50">
            <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-xl flex items-center justify-center mb-4">
              <HiOutlineStar size={24} />
            </div>
            <h3 className="text-lg font-bold text-skynest-navy mb-2">Create SkyNest Membership</h3>
            <p className="text-sm text-gray-500 mb-6">Enroll a guest into the SkyNest membership program to apply automatic discounts to their current and future stays.</p>
            <button onClick={handleCreateMembershipClick} className="w-full py-3 bg-skynest-navy text-white font-semibold rounded-xl hover:bg-skynest-blue transition-colors flex justify-center items-center gap-2">
              <HiOutlineUserAdd size={18} /> Enroll New Member
            </button>
          </div>

          <div className="bg-white/80 backdrop-blur-md p-8 rounded-2xl shadow-sm border border-white/50">
            <div className="w-12 h-12 bg-skynest-blue/10 text-skynest-blue rounded-xl flex items-center justify-center mb-4">
              <HiOutlineSearch size={24} />
            </div>
            <h3 className="text-lg font-bold text-skynest-navy mb-2">Search Guest Records</h3>
            <p className="text-sm text-gray-500 mb-6">Look up previous bookings, previous payments, and historical data for returning guests.</p>
            <div className="flex gap-2">
              <input 
                type="text" 
                placeholder="Enter Guest ID or Phone" 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-skynest-blue" 
              />
              <button onClick={handleCheckPaymentStatus} className="px-6 py-3 bg-skynest-blue text-white font-semibold rounded-xl hover:bg-skynest-blue-hover transition-colors">
                Search
              </button>
            </div>
          </div>
        </div>
      )}

      {isMembershipModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-scale-up">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-amber-100 text-amber-600 rounded-lg flex items-center justify-center">
                  <HiOutlineStar size={20} />
                </div>
                <div>
                  <h3 className="font-bold text-skynest-navy">New SkyNest Member</h3>
                  <p className="text-xs text-gray-500">Enroll guest in loyalty program</p>
                </div>
              </div>
              <button 
                type="button"
                onClick={(e) => { e.stopPropagation(); setIsMembershipModalOpen(false); }}
                className="p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-200 rounded-full transition-colors relative z-50"
              >
                <HiX size={20} className="pointer-events-none" />
              </button>
            </div>
            
            <form onSubmit={submitMembership} className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-bold text-skynest-navy mb-1">Full Name</label>
                  <div className="relative">
                    <HiOutlineUser className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input 
                      type="text" 
                      required
                      value={membershipData.name}
                      onChange={(e) => setMembershipData({...membershipData, name: e.target.value})}
                      className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-skynest-blue"
                      placeholder="e.g. John Doe"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-skynest-navy mb-1">Phone Number</label>
                  <div className="relative">
                    <HiOutlinePhone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input 
                      type="tel" 
                      required
                      value={membershipData.phone}
                      onChange={(e) => setMembershipData({...membershipData, phone: e.target.value})}
                      className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-skynest-blue"
                      placeholder="+94 7X XXX XXXX"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-bold text-skynest-navy mb-1">Email Address</label>
                  <div className="relative">
                    <HiOutlineMail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input 
                      type="email" 
                      required
                      value={membershipData.email}
                      onChange={(e) => setMembershipData({...membershipData, email: e.target.value})}
                      className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-skynest-blue"
                      placeholder="john@example.com"
                    />
                  </div>
                </div>
              </div>

              <div className="mt-8 flex gap-3">
                <button 
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setIsMembershipModalOpen(false); }}
                  className="flex-1 py-3 bg-gray-100 hover:bg-gray-200 text-skynest-navy font-bold rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1 py-3 bg-skynest-blue text-white font-bold rounded-xl hover:bg-skynest-blue-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? 'Enrolling...' : 'Confirm Enrollment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {isPaymentModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm overflow-hidden animate-scale-up">
            <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
              <h3 className="font-bold text-skynest-navy">Guest Records</h3>
              <button 
                type="button"
                onClick={(e) => { e.stopPropagation(); setIsPaymentModalOpen(false); }}
                className="p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-200 rounded-full transition-colors relative z-50"
              >
                <HiX size={20} className="pointer-events-none" />
              </button>
            </div>
            
            <div className="p-8 flex flex-col items-center text-center">
              {paymentStatus === 'LOADING' ? (
                <>
                  <div className="w-12 h-12 border-4 border-skynest-blue border-t-transparent rounded-full animate-spin mb-4"></div>
                  <h4 className="font-bold text-skynest-navy mb-2">Searching Records</h4>
                  <p className="text-sm text-gray-500">Retrieving previous bookings and payment status...</p>
                </>
              ) : (
                <>
                  <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
                    <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h4 className="font-bold text-skynest-navy mb-2">PAID IN FULL</h4>
                  <p className="text-sm text-gray-500 mb-6">No outstanding balances found for {searchQuery || 'this guest'}.</p>
                  
                  <button 
                    onClick={() => setIsPaymentModalOpen(false)}
                    className="w-full py-3 bg-skynest-navy text-white font-bold rounded-xl hover:bg-skynest-blue transition-colors"
                  >
                    Close
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
