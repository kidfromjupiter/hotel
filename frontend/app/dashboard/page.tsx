'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getMyBookings } from '@/lib/api';
import type { StaffBooking } from '@/lib/types';
import toast from 'react-hot-toast';

export default function GuestDashboard() {
  const router = useRouter();
  const [bookings, setBookings] = useState<StaffBooking[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('guest_token');
    if (!token) {
      router.replace('/login');
      return;
    }

    const fetchBookings = async () => {
      try {
        const data = await getMyBookings();
        setBookings(data);
      } catch (err: any) {
        toast.error('Failed to load your bookings');
        if (err.message?.includes('401')) {
          localStorage.removeItem('guest_token');
          router.replace('/login');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchBookings();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('guest_token');
    router.replace('/');
  };

  return (
    <div className="min-h-screen bg-skynest-blue-pale pt-24 pb-12">
      <div className="max-w-5xl mx-auto px-4">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-black text-skynest-navy tracking-wide">MY ACCOUNT</h1>
          <button
            onClick={handleLogout}
            className="text-sm font-bold tracking-widest text-red-600 hover:text-red-800 transition-colors"
          >
            LOGOUT
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-xl font-bold text-skynest-navy mb-4">My Bookings</h2>
          {loading ? (
            <p className="text-gray-500">Loading your reservations...</p>
          ) : bookings.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 mb-4">You have no upcoming or past reservations.</p>
              <Link
                href="/booking"
                className="inline-block bg-skynest-blue text-white px-6 py-3 font-bold tracking-widest rounded-sm hover:bg-skynest-blue-hover transition-colors"
              >
                BOOK A STAY
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="py-3 px-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Reference</th>
                    <th className="py-3 px-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Branch</th>
                    <th className="py-3 px-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Check In</th>
                    <th className="py-3 px-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Check Out</th>
                    <th className="py-3 px-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {bookings.map(b => (
                    <tr key={b.bookingId} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4 font-mono text-sm text-skynest-blue font-bold">{b.bookingReference}</td>
                      <td className="py-3 px-4 text-sm text-gray-800">{b.branchId === 1 ? 'Colombo' : b.branchId === 2 ? 'Kandy' : b.branchId === 3 ? 'Galle' : 'SkyNest Hotel'}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{new Date(b.checkIn).toLocaleDateString()}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{new Date(b.checkOut).toLocaleDateString()}</td>
                      <td className="py-3 px-4 text-sm">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          b.status === 'CONFIRMED' ? 'bg-green-100 text-green-700' :
                          b.status === 'CHECKED_IN' ? 'bg-blue-100 text-blue-700' :
                          b.status === 'CHECKED_OUT' ? 'bg-gray-100 text-gray-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {b.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
