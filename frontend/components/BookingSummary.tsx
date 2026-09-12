import Link from 'next/link';
import { HiCheckCircle, HiHome, HiPhone, HiCalendar, HiLocationMarker } from 'react-icons/hi';
import type { BookingWizardState } from '@/lib/types';

interface BookingSummaryProps {
  booking: BookingWizardState;
}

const LKR = (n: number) =>
  new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 0,
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

export default function BookingSummary({ booking }: BookingSummaryProps) {
  const addonsTotal = booking.selectedAmenities.reduce((s, a) => s + a.price, 0);

  return (
    <div className="max-w-2xl mx-auto animate-slide-up">

      {/* ── Success hero ── */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-100 mb-4 shadow-lg">
          <HiCheckCircle className="text-green-500 text-[3rem]" />
        </div>
        <h2 className="text-3xl font-black text-skynest-navy">Booking Confirmed!</h2>
        <p className="text-skynest-muted mt-2 text-sm">
          Your reservation at SkyNest has been successfully placed.
        </p>

        {/* Booking ref pill */}
        <div className="mt-5 inline-flex items-center gap-3 bg-skynest-navy rounded-full px-6 py-2.5 shadow-xl">
          <span className="text-skynest-blue-light text-xs tracking-wide">Booking Reference</span>
          <span className="text-white font-black text-lg tracking-[0.2em]">
            {booking.bookingRef}
          </span>
        </div>
      </div>

      {/* ── OTP Alert ── */}
      <div className="bg-amber-50 border-2 border-amber-400 rounded-2xl p-5 mb-6 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
            <HiPhone className="text-amber-600 text-xl" />
          </div>
          <div>
            <h3 className="font-black text-amber-800 mb-1">📱 Important — Keep Your OTP!</h3>
            <p className="text-amber-700 text-sm leading-relaxed">
              An OTP confirmation message has been sent to{' '}
              <strong>{booking.phone}</strong>.{' '}
              <span className="font-bold">Please save this OTP message</span> — you must
              present it to the receptionist upon arrival at the hotel as your proof of booking.
              Do not delete the SMS.
            </p>
          </div>
        </div>
      </div>

      {/* ── Booking details card ── */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-5">
        <div className="bg-skynest-navy px-6 py-4 flex items-center gap-2">
          <HiCalendar className="text-skynest-blue" />
          <h3 className="text-white font-bold text-xs tracking-[0.15em]">BOOKING DETAILS</h3>
        </div>
        <div className="px-6 py-5 divide-y divide-gray-50">
          {[
            {
              label: 'Property',
              value: BRANCH_LABELS[booking.branch] ?? booking.branch,
              icon: <HiLocationMarker className="text-skynest-blue" />,
            },
            { label: 'Check-in', value: fmtDate(booking.checkIn) },
            { label: 'Check-out', value: fmtDate(booking.checkOut) },
            {
              label: 'Duration',
              value: `${booking.nights} night${booking.nights !== 1 ? 's' : ''}`,
            },
            {
              label: 'Guests',
              value: [
                `${booking.adults} adult${booking.adults !== 1 ? 's' : ''}`,
                booking.children > 0
                  ? `${booking.children} child${booking.children !== 1 ? 'ren' : ''}`
                  : null,
              ]
                .filter(Boolean)
                .join(' + '),
            },
            {
              label: 'Room',
              value: booking.selectedRoom?.name ?? '—',
            },
            { label: 'Contact', value: booking.phone },
          ].map(row => (
            <div
              key={row.label}
              className="flex items-center justify-between py-3 gap-4"
            >
              <span className="text-xs text-skynest-muted font-semibold tracking-wide uppercase w-24 flex-shrink-0">
                {row.label}
              </span>
              <span className="text-sm font-semibold text-skynest-navy text-right">
                {row.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Price breakdown card ── */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-8">
        <div className="bg-skynest-navy px-6 py-4">
          <h3 className="text-white font-bold text-xs tracking-[0.15em]">PRICE BREAKDOWN</h3>
        </div>
        <div className="px-6 py-5 space-y-3 text-sm">
          {booking.selectedRoom && (
            <div className="flex justify-between text-gray-600">
              <span>
                {booking.selectedRoom.name}{' '}
                <span className="text-xs text-skynest-muted">
                  × {booking.nights} night{booking.nights !== 1 ? 's' : ''}
                </span>
              </span>
              <span className="font-medium text-skynest-navy">
                {LKR(booking.selectedRoom.totalPrice)}
              </span>
            </div>
          )}

          {booking.selectedAmenities.map(a => (
            <div key={a.id} className="flex justify-between text-gray-600">
              <span className="flex items-center gap-1.5">
                <span>{a.icon}</span> {a.name}
              </span>
              <span className="font-medium text-skynest-navy">{LKR(a.price)}</span>
            </div>
          ))}

          {booking.hasMembership && (
            <div className="flex justify-between text-amber-600 font-semibold">
              <span>⭐ SkyNest Member Discount</span>
              <span>Applied</span>
            </div>
          )}

          <div className="border-t-2 border-dashed border-gray-100 pt-3 flex justify-between font-black text-base">
            <span className="text-skynest-navy">Total Amount</span>
            <span className="text-skynest-blue">{LKR(booking.totalPrice)}</span>
          </div>
        </div>
      </div>

      {/* ── Actions ── */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link
          href="/"
          className="flex items-center justify-center gap-2 px-8 py-3 bg-skynest-navy text-white font-bold text-sm rounded-xl hover:bg-skynest-blue transition-colors tracking-wide"
        >
          <HiHome /> Back to Home
        </Link>
        <button
          onClick={() => window.print()}
          className="flex items-center justify-center gap-2 px-8 py-3 border-2 border-skynest-navy text-skynest-navy font-bold text-sm rounded-xl hover:bg-skynest-blue-pale transition-colors tracking-wide"
        >
          🖨️ Print Summary
        </button>
      </div>
    </div>
  );
}
