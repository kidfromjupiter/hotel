'use client';

import Link from 'next/link';
import { HiCheckCircle, HiHome, HiPhone, HiCalendar } from 'react-icons/hi';
import type { BookingWizardState } from '@/lib/types';

interface BookingConfirmedProps {
  booking: BookingWizardState;
}

const LKR = (n: number) =>
  new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n);

const fmtDate = (d: string) =>
  new Date(d).toLocaleDateString('en-LK', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

const BRANCH_LABELS: Record<string, string> = {
  colombo: 'SkyNest Colombo',
  kandy: 'SkyNest Kandy',
  galle: 'SkyNest Galle',
};

export default function BookingConfirmed({ booking }: BookingConfirmedProps) {
  const branchTitle = BRANCH_LABELS[booking.branch] ?? booking.branch;

  return (
    <div className="max-w-2xl mx-auto animate-slide-up booking-print-container print:max-w-full print:mx-auto print:p-0">

      {/* ── Luxury Print-Only Voucher Header ── */}
      <div className="hidden print:flex items-center justify-between pb-3 mb-3 border-b-2 border-skynest-navy">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xl font-black tracking-[0.2em] text-skynest-navy">SKYNEST</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-sky-100 text-sky-800 tracking-wider">OFFICIAL VOUCHER</span>
          </div>
          <p className="text-[10px] text-gray-500 tracking-[0.2em] uppercase font-semibold mt-0.5">
            Hotels & Resorts · {branchTitle}
          </p>
        </div>
        <div className="text-right">
          <span className="text-[10px] text-gray-400 uppercase tracking-widest block font-mono">Reference</span>
          <span className="text-base font-black tracking-[0.15em] text-skynest-navy font-mono">
            {booking.bookingRef || 'SKN-CONFIRMED'}
          </span>
        </div>
      </div>

      {/* ── Success Hero (Screen only) ── */}
      <div className="text-center mb-8 print:hidden">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-100 mb-4 shadow-lg">
          <HiCheckCircle className="text-green-500 text-[3rem]" />
        </div>
        <h2 className="text-3xl font-black text-skynest-navy">Booking Confirmed!</h2>
        <p className="text-skynest-muted mt-2 text-sm">
          Your reservation at SkyNest has been successfully created.
        </p>

        {/* Booking Reference Badge */}
        <div className="mt-5 inline-flex items-center gap-3 bg-skynest-navy rounded-full px-6 py-2.5 shadow-xl">
          <span className="text-skynest-blue-light text-xs tracking-wide">Booking Reference</span>
          <span className="text-white font-black text-lg tracking-[0.2em]">
            {booking.bookingRef || 'SKN-CONFIRMED'}
          </span>
        </div>
      </div>

      {/* ── Prominent OTP Notice for Receptionist ── */}
      <div className="bg-amber-50 border-2 border-amber-400 rounded-2xl p-5 mb-6 shadow-md print:p-3 print:mb-3 print:border print:border-amber-400 print:rounded-xl print:shadow-none">
        <div className="flex items-start gap-4 print:gap-3">
          <div className="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0 print:w-9 print:h-9">
            <HiPhone className="text-amber-600 text-2xl print:text-lg" />
          </div>
          <div>
            <h3 className="font-black text-amber-900 text-base mb-1 print:text-sm print:mb-0.5">📱 Important: Keep Your OTP Message!</h3>
            <p className="text-amber-800 text-sm leading-relaxed print:text-xs print:leading-snug">
              An OTP confirmation SMS has been dispatched to <strong>{booking.phone}</strong>.
              <br />
              <span className="font-bold underline">Please do not delete that SMS</span>. When you arrive at the hotel, show this OTP message to the receptionist to verify your reservation and receive your room key.
            </p>
          </div>
        </div>
      </div>

      {/* ── Compact Booking Overview ── */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-6 print:border print:border-gray-200 print:rounded-xl print:mb-3 print:shadow-none">
        <div className="bg-skynest-navy px-6 py-4 flex items-center gap-2 print:px-4 print:py-2.5">
          <HiCalendar className="text-skynest-blue print:text-xs" />
          <h3 className="text-white font-bold text-xs tracking-[0.15em] print:text-[11px]">RESERVATION DETAILS</h3>
        </div>
        <div className="px-6 py-5 divide-y divide-gray-100 text-sm print:px-4 print:py-3 print:text-xs">
          <div className="flex justify-between py-2.5 print:py-1.5">
            <span className="text-gray-500 font-medium">Branch</span>
            <span className="font-bold text-skynest-navy">{branchTitle}</span>
          </div>
          <div className="flex justify-between py-2.5 print:py-1.5">
            <span className="text-gray-500 font-medium">Check-in</span>
            <span className="font-semibold text-skynest-navy">{fmtDate(booking.checkIn)}</span>
          </div>
          <div className="flex justify-between py-2.5 print:py-1.5">
            <span className="text-gray-500 font-medium">Check-out</span>
            <span className="font-semibold text-skynest-navy">{fmtDate(booking.checkOut)}</span>
          </div>
          <div className="flex justify-between py-2.5 print:py-1.5">
            <span className="text-gray-500 font-medium">Guests</span>
            <span className="font-semibold text-skynest-navy">
              {booking.adults} Adult{booking.adults !== 1 ? 's' : ''}
              {booking.children > 0 ? ` + ${booking.children} Child${booking.children !== 1 ? 'ren' : ''}` : ''}
            </span>
          </div>
          <div className="flex justify-between py-2.5 print:py-1.5">
            <span className="text-gray-500 font-medium">Room Type</span>
            <span className="font-bold text-skynest-blue">{booking.selectedRoom?.name ?? 'Standard Room'}</span>
          </div>
          <div className="flex justify-between py-2.5 print:py-1.5">
            <span className="text-gray-500 font-medium">Contact Phone</span>
            <span className="font-semibold text-skynest-navy">{booking.phone}</span>
          </div>
          <div className="flex justify-between py-3 border-t-2 border-dashed border-gray-200 print:py-2.5">
            <span className="font-bold text-skynest-navy">Total Paid / Due</span>
            <span className="font-black text-skynest-blue text-lg print:text-sm">{LKR(booking.totalPrice)}</span>
          </div>
        </div>
      </div>

      {/* ── Print-only Guarantee & Verification Footer ── */}
      <div className="hidden print:flex items-center justify-between pt-2 border-t border-gray-200 text-[10px] text-gray-500 mb-2">
        <span>Thank you for choosing SkyNest Hotels. Present your OTP upon check-in.</span>
        <span>Issued on {new Date().toLocaleDateString('en-LK')}</span>
      </div>

      {/* ── Actions (Screen only) ── */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center print:hidden">
        <Link
          href="/"
          className="flex items-center justify-center gap-2 px-8 py-3.5 bg-skynest-navy text-white font-bold text-sm rounded-xl hover:bg-skynest-blue transition-colors tracking-wide shadow-md"
        >
          <HiHome size={16} /> Back to Home
        </Link>
        <button
          onClick={() => window.print()}
          className="flex items-center justify-center gap-2 px-8 py-3.5 border-2 border-skynest-navy text-skynest-navy font-bold text-sm rounded-xl hover:bg-white transition-colors tracking-wide cursor-pointer"
        >
          🖨️ Print Summary
        </button>
      </div>

    </div>
  );
}
