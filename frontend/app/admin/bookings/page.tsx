'use client';

import { useState, useEffect } from 'react';
import { HiOutlineEye, HiOutlineDownload, HiOutlineX } from 'react-icons/hi';
import { getAdminReservationsList } from '@/lib/api';
import type { AdminReservationListItem } from '@/lib/types';

export default function AdminBookingsPage() {
  const [bookings, setBookings] = useState<AdminReservationListItem[]>([]);
  const [filterStatus, setFilterStatus] = useState('All');
  const [selectedBooking, setSelectedBooking] = useState<AdminReservationListItem | null>(null);

  useEffect(() => {
    fetchBookings();
  }, [filterStatus]);

  const fetchBookings = async () => {
    const status = filterStatus === 'All' ? undefined : filterStatus;
    try {
      const data = await getAdminReservationsList(status);
      setBookings(data);
    } catch (error) {
      console.error("Error fetching admin reservations", error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'CONFIRMED': return 'bg-blue-100 text-blue-700';
      case 'CHECKED-IN': return 'bg-green-100 text-green-700';
      case 'CHECKED-OUT': return 'bg-slate-200 text-slate-700';
      case 'CANCELLED': return 'bg-red-100 text-red-700';
      default: return 'bg-slate-100 text-slate-700';
    }
  };

  const getInvoiceStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'PAID': return 'bg-emerald-100 text-emerald-700 border border-emerald-200';
      case 'PARTIAL': return 'bg-amber-100 text-amber-700 border border-amber-200';
      case 'UNPAID': return 'bg-rose-100 text-rose-700 border border-rose-200';
      default: return 'bg-slate-100 text-slate-700 border border-slate-200';
    }
  };

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || '?';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Booking Management & Invoices</h1>
          <p className="text-sm text-slate-600 mt-1 font-medium">View all reservations and financial breakdowns.</p>
        </div>
      </div>

      <div className="bg-white/80 backdrop-blur-md border border-white/40 shadow-xl shadow-slate-200/50 rounded-2xl overflow-hidden">
        <div className="p-6 border-b border-slate-200/50 bg-slate-50/50 flex justify-between items-center">
          <h3 className="font-bold text-slate-800">All Reservations</h3>
          <div className="flex gap-2">
            <select 
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 outline-none"
            >
              <option value="All">All Statuses</option>
              <option value="Confirmed">Confirmed</option>
              <option value="Checked-In">Checked-In</option>
              <option value="Checked-Out">Checked-Out</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-100/30 text-slate-500 text-xs uppercase tracking-wider">
                <th className="p-4 font-bold">Guest Info</th>
                <th className="p-4 font-bold">Room & Dates</th>
                <th className="p-4 font-bold">Finances</th>
                <th className="p-4 font-bold">Status</th>
                <th className="p-4 font-bold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {bookings.map((booking) => (
                <tr key={booking.booking_id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-sm">
                        {getInitials(booking.guest_name)}
                      </div>
                      <div>
                        <div className="font-bold text-slate-800">{booking.guest_name}</div>
                        <div className="text-xs text-slate-500 font-medium">Ref: BKG-{booking.booking_id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="font-bold text-slate-800">Room {booking.room_number}</div>
                    <div className="text-xs text-slate-500 font-medium">
                      {booking.start_date} to {booking.end_date} ({booking.nights} {booking.nights === 1 ? 'night' : 'nights'})
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-500">Total:</span>
                        <span className="font-bold text-slate-800">Rs {booking.grand_total.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-500">Paid:</span>
                        <span className="font-bold text-emerald-600">Rs {booking.amount_paid.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between text-xs mt-1 pt-1 border-t border-slate-100">
                        <span className="text-slate-500">Balance:</span>
                        <span className="font-bold text-rose-600">Rs {booking.balance_amount.toLocaleString()}</span>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex flex-col gap-2 items-start">
                      <span className={`px-2.5 py-1 rounded-md text-xs font-bold ${getStatusColor(booking.booking_status)}`}>
                        {booking.booking_status}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider ${getInvoiceStatusColor(booking.invoice_status)}`}>
                        {booking.invoice_status}
                      </span>
                    </div>
                  </td>
                  <td className="p-4 text-right">
                    <div className="flex justify-end gap-2">
                      <button 
                        onClick={() => setSelectedBooking(booking)}
                        className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors title='View Details'"
                      >
                        <HiOutlineEye size={20} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {bookings.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-slate-500">
                    No reservations found matching the filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* View Details Modal */}
      {selectedBooking && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
            
            <div className="px-6 py-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <div>
                <h2 className="text-xl font-bold text-slate-800">Booking Details</h2>
                <p className="text-sm text-slate-500 font-medium">Ref: BKG-{selectedBooking.booking_id}</p>
              </div>
              <button 
                onClick={() => setSelectedBooking(null)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-200/50 rounded-full transition-colors"
              >
                <HiOutlineX size={24} />
              </button>
            </div>

            <div className="p-6 overflow-y-auto">
              <div className="grid grid-cols-2 gap-6 mb-8">
                <div className="space-y-4">
                  <div>
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Guest Details</div>
                    <div className="font-bold text-slate-800 text-lg">{selectedBooking.guest_name}</div>
                    <div className="text-sm text-slate-600">{selectedBooking.guest_contact || 'No contact provided'}</div>
                    <div className="text-sm text-slate-600 mt-1">Guests: {selectedBooking.adult_count} Adults, {selectedBooking.children_count} Children</div>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Stay Info</div>
                    <div className="font-bold text-slate-800">Room {selectedBooking.room_number}</div>
                    <div className="text-sm text-slate-600">{selectedBooking.start_date} to {selectedBooking.end_date}</div>
                    <div className="text-sm text-slate-600">{selectedBooking.nights} {selectedBooking.nights === 1 ? 'night' : 'nights'} at {selectedBooking.branch_name}</div>
                  </div>
                </div>
                
                <div className="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Financial Summary</div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center text-sm text-slate-600">
                      <span>Room Charges</span>
                      <span className="font-medium">Rs {selectedBooking.total_room_charges.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm text-slate-600">
                      <span>Service Charges</span>
                      <span className="font-medium">Rs {selectedBooking.total_service_charges.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm text-slate-600">
                      <span>Taxes</span>
                      <span className="font-medium">Rs {selectedBooking.total_tax_amount.toLocaleString()}</span>
                    </div>
                    
                    <div className="pt-2 mt-2 border-t border-slate-200 border-dashed flex justify-between items-center">
                      <span className="text-sm text-slate-800 font-bold">Grand Total</span>
                      <span className="font-bold text-slate-800">Rs {selectedBooking.grand_total.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center text-emerald-600">
                      <span className="text-sm font-medium">Amount Paid {selectedBooking.payment_method !== 'NONE' && `(${selectedBooking.payment_method})`}</span>
                      <span className="font-bold">Rs {selectedBooking.amount_paid.toLocaleString()}</span>
                    </div>
                    <div className="pt-3 mt-3 border-t border-slate-200 flex justify-between items-center">
                      <span className="text-sm font-bold text-slate-800">Balance Due</span>
                      <span className="font-black text-rose-600 text-lg">Rs {selectedBooking.balance_amount.toLocaleString()}</span>
                    </div>
                  </div>

                  <div className="mt-6 flex justify-between items-center">
                    <span className={`px-2.5 py-1 rounded-md text-xs font-bold ${getStatusColor(selectedBooking.booking_status)}`}>
                      {selectedBooking.booking_status}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider ${getInvoiceStatusColor(selectedBooking.invoice_status)}`}>
                      {selectedBooking.invoice_status}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="px-6 py-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
              <button 
                onClick={() => setSelectedBooking(null)}
                className="px-5 py-2 text-sm font-bold text-slate-600 hover:text-slate-900 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl transition-colors"
              >
                Close
              </button>
              <button 
                className="px-5 py-2 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-md transition-colors flex items-center gap-2"
              >
                <HiOutlineDownload size={18} />
                Download Invoice
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
