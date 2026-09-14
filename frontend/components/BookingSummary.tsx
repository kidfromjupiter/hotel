'use client';

import { HiCalendar, HiLocationMarker, HiUserGroup, HiArrowLeft, HiArrowRight, HiSparkles } from 'react-icons/hi';
import type { BookingWizardState } from '@/lib/types';

interface BookingSummaryProps {
  booking: BookingWizardState;
  onBack: () => void;
  onContinue: () => void;
}

const LKR = (n: number) =>
  new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n);

const fmtDate = (d: string) => {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-LK', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const BRANCH_LABELS: Record<string, string> = {
  colombo: 'SkyNest Colombo',
  kandy: 'SkyNest Kandy',
  galle: 'SkyNest Galle',
};

export default function BookingSummary({ booking, onBack, onContinue }: BookingSummaryProps) {
  const room = booking.selectedRoom;
  const roomPricePerNight = booking.hasMembership && room?.membershipPrice ? room.membershipPrice : (room?.pricePerNight ?? 0);
  const roomTotal = roomPricePerNight * (booking.nights || 1);
  const amenitiesTotal = booking.selectedAmenities.reduce((sum, item) => sum + item.price, 0);
  const calculatedGrandTotal = roomTotal + amenitiesTotal;

  return (
    <div className="max-w-3xl mx-auto animate-slide-up">
      {/* ── Top Header ── */}
      <div className="mb-6">
        <p className="text-skynest-blue text-xs tracking-[0.2em] font-bold mb-1 uppercase">STEP 4 OF 6</p>
        <h2 className="text-2xl sm:text-3xl font-black text-skynest-navy">Booking Summary &amp; Review</h2>
        <p className="text-skynest-muted text-sm mt-1">
          Please review your booking details below before proceeding to confirm your reservation.
        </p>
      </div>

      {/* ── Summary Card ── */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-xl overflow-hidden mb-6">
        
        {/* Banner */}
        <div className="bg-skynest-navy px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-2 text-white">
            <HiLocationMarker className="text-skynest-blue text-xl flex-shrink-0" />
            <span className="font-bold text-base tracking-wide">
              {BRANCH_LABELS[booking.branch] ?? `SkyNest ${booking.branch}`}
            </span>
          </div>
          <span className="bg-skynest-blue/20 text-skynest-blue-light border border-skynest-blue/30 text-xs px-3 py-1 rounded-full font-semibold">
            {booking.nights} Night{booking.nights !== 1 ? 's' : ''} Stay
          </span>
        </div>

        <div className="p-6 sm:p-8 space-y-6 divide-y divide-gray-100">

          {/* Dates & Guests Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pb-2">
            
            {/* Stay Dates */}
            <div className="bg-skynest-blue-pale rounded-xl p-4 border border-skynest-blue/10">
              <div className="flex items-center gap-2 text-skynest-blue mb-2">
                <HiCalendar size={18} />
                <span className="text-xs font-bold tracking-wider uppercase text-skynest-navy">STAY DATES</span>
              </div>
              <div className="text-sm space-y-1">
                <div className="flex justify-between">
                  <span className="text-gray-500">Check-in:</span>
                  <span className="font-bold text-skynest-navy">{fmtDate(booking.checkIn)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Check-out:</span>
                  <span className="font-bold text-skynest-navy">{fmtDate(booking.checkOut)}</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-skynest-blue/10 text-xs">
                  <span className="text-gray-500">Total Duration:</span>
                  <span className="font-semibold text-skynest-blue">{booking.nights} night{booking.nights !== 1 ? 's' : ''}</span>
                </div>
              </div>
            </div>

            {/* Guests */}
            <div className="bg-skynest-blue-pale rounded-xl p-4 border border-skynest-blue/10">
              <div className="flex items-center gap-2 text-skynest-blue mb-2">
                <HiUserGroup size={18} />
                <span className="text-xs font-bold tracking-wider uppercase text-skynest-navy">GUESTS</span>
              </div>
              <div className="text-sm space-y-1">
                <div className="flex justify-between">
                  <span className="text-gray-500">Adults:</span>
                  <span className="font-bold text-skynest-navy">{booking.adults} Adult{booking.adults !== 1 ? 's' : ''}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Children:</span>
                  <span className="font-bold text-skynest-navy">{booking.children} Child{booking.children !== 1 ? 'ren' : ''}</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-skynest-blue/10 text-xs">
                  <span className="text-gray-500">Total Occupancy:</span>
                  <span className="font-semibold text-skynest-blue">{booking.adults + booking.children} Guest{booking.adults + booking.children !== 1 ? 's' : ''}</span>
                </div>
              </div>
            </div>

          </div>

          {/* Selected Room Details */}
          <div className="pt-4">
            <h4 className="text-xs font-bold text-gray-400 tracking-widest uppercase mb-3">SELECTED ROOM</h4>
            <div className="flex items-start justify-between bg-gray-50 rounded-xl p-4 border border-gray-200">
              <div>
                <span className="text-[11px] font-bold text-skynest-blue uppercase tracking-wider">{room?.type ?? 'Standard Room'}</span>
                <p className="text-base font-bold text-skynest-navy mt-0.5">{room?.name ?? 'Standard Room'}</p>
                <p className="text-xs text-skynest-muted mt-1 max-w-md line-clamp-1">{room?.description}</p>
                <p className="text-xs text-gray-500 mt-2">
                  Rate: <span className="font-semibold text-skynest-navy">{LKR(roomPricePerNight)}</span> / night × {booking.nights} night{booking.nights !== 1 ? 's' : ''}
                </p>
              </div>
              <div className="text-right flex-shrink-0">
                <span className="text-base font-black text-skynest-navy">{LKR(roomTotal)}</span>
              </div>
            </div>
          </div>

          {/* Extra Selected Amenities */}
          <div className="pt-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-xs font-bold text-gray-400 tracking-widest uppercase">ADDITIONAL AMENITIES</h4>
              <span className="text-xs text-skynest-blue font-semibold">
                {booking.selectedAmenities.length} selected
              </span>
            </div>

            {booking.selectedAmenities.length === 0 ? (
              <p className="text-xs text-gray-400 italic bg-gray-50 p-3 rounded-lg border border-dashed border-gray-200">
                No additional amenities selected.
              </p>
            ) : (
              <div className="space-y-2">
                {booking.selectedAmenities.map(amenity => (
                  <div key={amenity.id} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg text-sm border border-gray-100">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{amenity.icon}</span>
                      <div>
                        <p className="font-semibold text-skynest-navy text-xs sm:text-sm">{amenity.name}</p>
                        <p className="text-[11px] text-gray-400">{amenity.description}</p>
                      </div>
                    </div>
                    <span className="font-bold text-skynest-navy text-xs sm:text-sm">{LKR(amenity.price)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Price Calculation Breakdown */}
          <div className="pt-4 space-y-2.5">
            <h4 className="text-xs font-bold text-gray-400 tracking-widest uppercase mb-2">PRICE BREAKDOWN</h4>
            
            <div className="flex justify-between text-sm text-gray-600">
              <span>Room charges ({booking.nights} night{booking.nights !== 1 ? 's' : ''})</span>
              <span className="font-semibold text-skynest-navy">{LKR(roomTotal)}</span>
            </div>

            {amenitiesTotal > 0 && (
              <div className="flex justify-between text-sm text-gray-600">
                <span>Extra amenities total</span>
                <span className="font-semibold text-skynest-navy">{LKR(amenitiesTotal)}</span>
              </div>
            )}

            {booking.hasMembership && (
              <div className="flex justify-between text-sm text-amber-600 font-semibold">
                <span className="flex items-center gap-1"><HiSparkles /> SkyNest Member Exclusive Benefit</span>
                <span>Applied</span>
              </div>
            )}

            {/* Total */}
            <div className="border-t-2 border-dashed border-gray-200 pt-3 mt-3 flex items-center justify-between">
              <div>
                <span className="text-base font-black text-skynest-navy">Calculated Total</span>
                <p className="text-xs text-gray-400">All applicable taxes included</p>
              </div>
              <span className="text-2xl font-black text-skynest-blue">{LKR(calculatedGrandTotal)}</span>
            </div>
          </div>

        </div>
      </div>

      {/* ── Action Buttons ── */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <button
          type="button"
          onClick={onBack}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 border-2 border-skynest-navy text-skynest-navy font-bold text-sm rounded-xl hover:bg-white transition-colors"
        >
          <HiArrowLeft size={16} /> Go Back &amp; Change
        </button>

        <button
          type="button"
          onClick={onContinue}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-skynest-blue text-white font-black text-sm tracking-[0.1em] rounded-xl hover:bg-skynest-blue-hover transition-colors shadow-lg shadow-skynest-blue/30"
        >
          <span>Continue</span>
          <HiArrowRight size={16} />
        </button>
      </div>
    </div>
  );
}
