'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { HiOutlineKey, HiCheckCircle, HiXCircle } from 'react-icons/hi';

import { getAllBookings, checkInGuest } from '@/lib/api';
import type { StaffBooking } from '@/lib/types';

export default function CheckInPage() {
  const router = useRouter();
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bookingData, setBookingData] = useState<StaffBooking | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp) return;
    
    setLoading(true);
    setError(null);
    setBookingData(null);

    try {
      const allBookings = await getAllBookings();
      const match = allBookings.find(b => 
        b.bookingReference.toLowerCase() === otp.toLowerCase() && 
        b.status === 'Booked' // Only allow checkin for 'Booked' status bookings
      );
      
      if (match) {
        setBookingData(match);
      } else {
        setError('Invalid Reference/OTP or booking is not in Booked status.');
      }
    } catch (err) {
      console.error(err);
      setError('Could not connect to database.');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    if (!bookingData) return;
    setLoading(true);
    try {
      const result = await checkInGuest(bookingData.bookingId);
      if (result.success) {
        alert('Database Updated:\n- checked_in_time = NOW()\n- booking_status = CHECKED_IN\n- room_status = OCCUPIED');
        router.push('/receptionist/stays');
      } else {
        alert(`Check-in blocked: ${result.message}`);
      }
    } catch (err) {
      alert('Failed to connect to database for check-in.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-[75vh] flex items-center justify-center -mx-8 -my-8 px-8 py-12 overflow-hidden bg-transparent">
      {/* Animated Background Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-skynest-blue/20 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
      <div className="absolute top-[-10%] right-[-10%] w-96 h-96 bg-blue-300/20 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-[-20%] left-[20%] w-96 h-96 bg-sky-200/20 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>

      <div className="relative z-10 w-full max-w-xl flex flex-col items-center animate-slide-up">
        
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-white border border-blue-100 text-skynest-blue rounded-3xl mx-auto flex items-center justify-center mb-6 shadow-2xl shadow-skynest-blue/20">
            <HiOutlineKey size={40} />
          </div>
          <h1 className="text-4xl font-black text-skynest-navy tracking-tight">Guest Check-In</h1>
          <p className="text-gray-500 mt-3 text-lg font-medium">
            Scan or enter the customer's OTP to retrieve booking details.
          </p>
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-[2rem] shadow-2xl shadow-skynest-navy/5 border border-white p-10 w-full relative overflow-hidden">
          {/* Decor */}
          <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-skynest-blue via-blue-400 to-skynest-navy"></div>

        {!bookingData ? (
          <form onSubmit={handleSearch} className="space-y-6">
            <div>
                <label className="block text-sm font-bold text-skynest-navy uppercase tracking-wider mb-3">
                  Booking Reference / OTP
                </label>
                <div className="relative">
                  <input 
                    type="text" 
                    value={otp}
                    onChange={e => setOtp(e.target.value)}
                    placeholder="e.g. BKG-123"
                    className="w-full text-center text-2xl font-black tracking-widest px-6 py-6 bg-gray-50/50 border-2 border-gray-200 rounded-2xl text-skynest-navy placeholder-gray-300 focus:outline-none focus:border-skynest-blue focus:bg-white focus:ring-4 focus:ring-skynest-blue/10 transition-all shadow-inner"
                  />
                </div>
            </div>
            
            {error && (
              <div className="bg-red-50 text-red-500 text-sm p-4 rounded-xl font-bold flex items-center justify-center gap-2">
                <HiXCircle size={20} /> {error}
              </div>
            )}

              <button 
                type="submit"
                disabled={loading || !otp}
                className="w-full py-5 bg-gradient-to-r from-skynest-navy to-skynest-blue text-white text-lg font-bold tracking-widest uppercase rounded-2xl hover:opacity-90 transition-all shadow-xl shadow-skynest-blue/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none relative overflow-hidden group"
              >
                <div className="absolute inset-0 w-full h-full bg-white/20 scale-x-0 group-hover:scale-x-100 origin-left transition-transform duration-500"></div>
                <span className="relative z-10">{loading ? 'Verifying...' : 'Verify OTP'}</span>
              </button>
          </form>
        ) : (
          <div className="animate-slide-up">
            <div className="flex items-center justify-center gap-2 text-skynest-blue mb-6">
              <HiCheckCircle size={28} />
              <span className="font-bold text-lg tracking-wide uppercase text-skynest-navy">Booking Verified</span>
            </div>

            <div className="bg-gray-50 rounded-2xl p-6 space-y-4 mb-6">
              <div className="flex justify-between items-center border-b border-gray-200 pb-4">
                <p className="text-sm text-gray-500 font-bold uppercase tracking-wider">Guest</p>
                <p className="font-black text-skynest-navy text-xl">{bookingData.guestName}</p>
              </div>
              <div className="flex justify-between items-center border-b border-gray-200 pb-4">
                <p className="text-sm text-gray-500 font-bold uppercase tracking-wider">Room</p>
                <div className="text-right">
                  <p className="font-black text-skynest-blue text-2xl">{bookingData.roomNumber}</p>
                  <p className="text-xs font-bold text-gray-500 uppercase">{bookingData.roomType}</p>
                </div>
              </div>
              <div className="flex justify-between items-center pb-2">
                <p className="text-sm text-gray-500 font-bold uppercase tracking-wider">Stay</p>
                <p className="font-bold text-skynest-navy">{bookingData.checkIn} to {bookingData.checkOut}</p>
              </div>
            </div>

              <div className="flex gap-4 mt-8">
                <button 
                  onClick={() => setBookingData(null)}
                  className="w-1/3 py-4 border-2 border-gray-200 text-gray-500 font-bold rounded-2xl hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleCheckIn}
                  className="w-2/3 py-4 bg-gradient-to-r from-skynest-blue to-[#00a8e8] text-white font-black tracking-wider uppercase rounded-2xl hover:opacity-90 transition-all shadow-xl shadow-skynest-blue/30"
                >
                  Check-In Guest
                </button>
              </div>
          </div>
        )}
        </div>
      </div>
    </div>
  );
}
