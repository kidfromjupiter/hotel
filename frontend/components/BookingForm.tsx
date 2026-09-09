'use client';

import { useState } from 'react';
import { HiCalendar, HiMinus, HiPlus, HiSearch } from 'react-icons/hi';

interface FormData {
  checkIn: string;
  checkOut: string;
  adults: number;
  children: number;
}

interface BookingFormProps {
  branchName: string;
  onSubmit: (data: FormData) => void;
  loading: boolean;
}

function GuestCounter({
  label,
  emoji,
  value,
  min,
  max,
  onChange,
}: {
  label: string;
  emoji: string;
  value: number;
  min: number;
  max: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex-1 bg-skynest-blue-pale rounded-xl p-4 border border-skynest-blue/10">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-base">{emoji}</span>
        <span className="text-sm font-semibold text-skynest-navy">{label}</span>
      </div>
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => onChange(Math.max(min, value - 1))}
          disabled={value <= min}
          className="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center text-skynest-muted hover:border-skynest-blue hover:text-skynest-blue transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <HiMinus size={14} />
        </button>
        <span className="text-2xl font-bold text-skynest-navy w-10 text-center">{value}</span>
        <button
          type="button"
          onClick={() => onChange(Math.min(max, value + 1))}
          disabled={value >= max}
          className="w-8 h-8 rounded-full bg-skynest-blue text-white flex items-center justify-center hover:bg-skynest-blue-hover transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <HiPlus size={14} />
        </button>
      </div>
    </div>
  );
}

export default function BookingForm({
  branchName,
  onSubmit,
  loading,
}: BookingFormProps) {
  const today = new Date().toISOString().split('T')[0];
  const tomorrow = new Date(Date.now() + 86_400_000).toISOString().split('T')[0];

  const [checkIn, setCheckIn] = useState(today);
  const [checkOut, setCheckOut] = useState(tomorrow);
  const [adults, setAdults] = useState(1);
  const [children, setChildren] = useState(0);
  const [errors, setErrors] = useState<Partial<Record<'checkIn' | 'checkOut', string>>>({});

  const validate = (): boolean => {
    const e: typeof errors = {};
    if (!checkIn) e.checkIn = 'Please select a check-in date.';
    if (!checkOut) e.checkOut = 'Please select a check-out date.';
    if (checkIn && checkOut && checkIn >= checkOut)
      e.checkOut = 'Check-out must be after check-in.';
    if (checkIn < today) e.checkIn = 'Check-in cannot be in the past.';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleCheckInChange = (value: string) => {
    setCheckIn(value);
    // Auto-advance check-out if it would be invalid
    if (value >= checkOut) {
      const next = new Date(value);
      next.setDate(next.getDate() + 1);
      setCheckOut(next.toISOString().split('T')[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({ checkIn, checkOut, adults, children });
  };

  // Derived: number of nights
  const nights =
    checkIn && checkOut && checkOut > checkIn
      ? Math.ceil(
          (new Date(checkOut).getTime() - new Date(checkIn).getTime()) / 86_400_000
        )
      : 0;

  return (
    <div className="max-w-2xl mx-auto animate-slide-up">
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden">

        {/* ── Card header ── */}
        <div className="bg-skynest-navy px-8 py-6">
          <p className="text-skynest-blue text-xs tracking-[0.2em] font-semibold mb-1">
            STEP 1 OF 5
          </p>
          <h2 className="text-2xl font-bold text-white">Booking Details</h2>
          <p className="text-gray-400 text-sm mt-1">SkyNest {branchName}</p>
        </div>

        <form onSubmit={handleSubmit} className="px-8 py-8 space-y-6">

          {/* ── Dates row ── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

            {/* Check-in */}
            <div>
              <label className="block text-xs font-bold text-skynest-navy tracking-[0.1em] mb-2 uppercase">
                Check-in Date
              </label>
              <div className="relative">
                <HiCalendar className="absolute left-3 top-1/2 -translate-y-1/2 text-skynest-blue text-lg pointer-events-none" />
                <input
                  type="date"
                  value={checkIn}
                  min={today}
                  onChange={e => handleCheckInChange(e.target.value)}
                  className={`w-full pl-10 pr-4 py-3 border rounded-xl text-skynest-navy text-sm focus:outline-none focus:ring-2 focus:ring-skynest-blue/50 transition-all ${
                    errors.checkIn ? 'border-red-400 bg-red-50' : 'border-gray-200 hover:border-skynest-blue/50'
                  }`}
                />
              </div>
              {errors.checkIn && (
                <p className="text-red-500 text-xs mt-1.5">{errors.checkIn}</p>
              )}
            </div>

            {/* Check-out */}
            <div>
              <label className="block text-xs font-bold text-skynest-navy tracking-[0.1em] mb-2 uppercase">
                Check-out Date
              </label>
              <div className="relative">
                <HiCalendar className="absolute left-3 top-1/2 -translate-y-1/2 text-skynest-blue text-lg pointer-events-none" />
                <input
                  type="date"
                  value={checkOut}
                  min={checkIn || today}
                  onChange={e => setCheckOut(e.target.value)}
                  className={`w-full pl-10 pr-4 py-3 border rounded-xl text-skynest-navy text-sm focus:outline-none focus:ring-2 focus:ring-skynest-blue/50 transition-all ${
                    errors.checkOut ? 'border-red-400 bg-red-50' : 'border-gray-200 hover:border-skynest-blue/50'
                  }`}
                />
              </div>
              {errors.checkOut && (
                <p className="text-red-500 text-xs mt-1.5">{errors.checkOut}</p>
              )}
            </div>
          </div>

          {/* Nights summary */}
          {nights > 0 && (
            <div className="flex items-center gap-2 px-4 py-2.5 bg-skynest-blue/10 border border-skynest-blue/20 rounded-xl">
              <span className="text-skynest-blue text-lg">🌙</span>
              <span className="text-sm font-semibold text-skynest-navy">
                {nights} night{nights !== 1 ? 's' : ''}
              </span>
              <span className="text-xs text-skynest-muted ml-1">selected</span>
            </div>
          )}

          {/* ── Divider ── */}
          <div className="border-t border-gray-100" />

          {/* ── Guests ── */}
          <div>
            <label className="block text-xs font-bold text-skynest-navy tracking-[0.1em] mb-3 uppercase">
              Number of Guests
            </label>
            <div className="flex gap-4">
              <GuestCounter
                label="Adults"
                emoji="👤"
                value={adults}
                min={1}
                max={10}
                onChange={setAdults}
              />
              <GuestCounter
                label="Children"
                emoji="🧒"
                value={children}
                min={0}
                max={10}
                onChange={setChildren}
              />
            </div>
            <p className="text-xs text-skynest-muted mt-2">
              Total: {adults + children} guest{adults + children !== 1 ? 's' : ''}
            </p>
          </div>

          {/* ── Submit ── */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-4 bg-skynest-blue text-white font-bold text-sm tracking-[0.15em] rounded-xl hover:bg-skynest-blue-hover transition-colors disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-skynest-blue/30"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Checking Availability...
              </>
            ) : (
              <>
                <HiSearch size={16} />
                CHECK AVAILABILITY
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
