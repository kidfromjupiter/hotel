'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { HiOutlineKey, HiCheckCircle, HiXCircle } from 'react-icons/hi';

const mockVerifyOTP = async (otp: string) => {
  return new Promise<any>((resolve) => {
    setTimeout(() => {
      if (otp === '123456') {
        resolve({
          success: true,
          booking: {
            id: 'BKG-9921',
            guestName: 'Kasun Perera',
            phone: '+94771234567',
            roomType: 'Deluxe Suite',
            roomNumber: '201',
            checkIn: '2026-09-24',
            checkOut: '2026-09-26',
            status: 'PENDING',
          }
        });
      } else {
        resolve({ success: false, message: 'Invalid OTP or booking not found.' });
      }
    }, 800);
  });
};

export default function CheckInPage() {
  const router = useRouter();
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bookingData, setBookingData] = useState<any | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp) return;
    
    setLoading(true);
    setError(null);
    setBookingData(null);

    const result = await mockVerifyOTP(otp);
    if (result.success) {
      setBookingData(result.booking);
    } else {
      setError(result.message);
    }
    setLoading(false);
  };

  const handleCheckIn = () => {
    alert('Database Updated:\n- checked_in_time = NOW()\n- booking_status = CHECKED_IN\n- room_status = OCCUPIED');
    // Transition to active stays
    router.push('/receptionist/stays');
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] animate-slide-up">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-skynest-navy text-skynest-blue rounded-2xl mx-auto flex items-center justify-center mb-4 shadow-xl">
          <HiOutlineKey size={32} />
        </div>
        <h1 className="text-3xl font-black text-skynest-navy">Guest Check-In</h1>
        <p className="text-gray-500 mt-2 max-w-md mx-auto">
          Scan or enter the customer's OTP to securely retrieve their booking details and complete the check-in process.
        </p>
      </div>

      <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 p-8 w-full max-w-lg relative overflow-hidden">
        {/* Decor */}
        <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-skynest-blue to-skynest-navy"></div>

        {!bookingData ? (
          <form onSubmit={handleSearch} className="space-y-6">
            <div>
              <label className="block text-xs font-black text-skynest-navy tracking-widest uppercase mb-2">
                Booking OTP
              </label>
              <input 
                type="text" 
                value={otp}
                onChange={e => setOtp(e.target.value)}
                placeholder="Enter 123456"
                className="w-full text-center text-3xl tracking-[0.5em] font-black px-4 py-6 bg-gray-50 border-2 border-gray-200 rounded-2xl text-skynest-navy focus:outline-none focus:border-skynest-blue focus:bg-white transition-all"
              />
            </div>
            
            {error && (
              <div className="bg-red-50 text-red-500 text-sm p-4 rounded-xl font-bold flex items-center justify-center gap-2">
                <HiXCircle size={20} /> {error}
              </div>
            )}

            <button 
              type="submit"
              disabled={loading || !otp}
              className="w-full py-5 bg-skynest-navy text-white text-lg font-black tracking-widest uppercase rounded-2xl hover:bg-skynest-blue transition-colors shadow-lg shadow-skynest-navy/20 disabled:opacity-50"
            >
              {loading ? 'Verifying OTP...' : 'Verify OTP'}
            </button>
          </form>
        ) : (
          <div className="animate-slide-up">
            <div className="flex items-center justify-center gap-2 text-green-500 mb-6">
              <HiCheckCircle size={28} />
              <span className="font-black text-lg tracking-wide uppercase">Booking Verified</span>
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

            <div className="flex gap-4">
              <button 
                onClick={() => setBookingData(null)}
                className="w-1/3 py-4 border-2 border-gray-200 text-gray-500 font-bold rounded-2xl hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={handleCheckIn}
                className="w-2/3 py-4 bg-green-500 text-white font-black tracking-wider uppercase rounded-2xl hover:bg-green-600 transition-colors shadow-lg shadow-green-500/30"
              >
                Check-In Guest
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
