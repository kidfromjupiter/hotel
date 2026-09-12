'use client';

import { useState } from 'react';
import { HiPhone, HiLockClosed, HiRefresh } from 'react-icons/hi';
import { sendOTP, verifyOTP, createBooking } from '@/lib/api';
import type { CreateBookingPayload } from '@/lib/types';
import toast from 'react-hot-toast';

interface PhoneOTPFormProps {
  /** Booking data minus the phone number (added here) */
  bookingData: Omit<CreateBookingPayload, 'phone'>;
  /** Called after OTP verified + booking created successfully */
  onComplete: (phone: string, bookingRef: string) => void;
}

type Mode = 'phone' | 'otp';

/** Strip leading 0 and format as +94XXXXXXXXX */
function toE164(local: string): string {
  const digits = local.replace(/\D/g, '');
  const stripped = digits.startsWith('0') ? digits.slice(1) : digits;
  return `+94${stripped}`;
}

export default function PhoneOTPForm({ bookingData, onComplete }: PhoneOTPFormProps) {
  const [mode, setMode] = useState<Mode>('phone');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fullPhone = toE164(phone);
  const phoneValid = phone.replace(/\D/g, '').length >= 9;

  // ── Step A: Send OTP ──────────────────────────────
  const handleSendOTP = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!phoneValid) {
      setError('Please enter a valid Sri Lankan phone number (9 digits).');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await sendOTP(fullPhone);
      if (res.success) {
        toast.success('OTP sent! Check your SMS.');
        setMode('otp');
      } else {
        setError(res.message ?? 'Failed to send OTP. Please try again.');
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to send OTP.';
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  // ── Step B: Verify OTP + create booking ──────────
  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    if (otp.trim().length < 4) {
      setError('Please enter the OTP sent to your phone.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. Verify OTP
      const verifyRes = await verifyOTP(fullPhone, otp.trim());
      if (!verifyRes.success) {
        setError(verifyRes.message ?? 'Invalid OTP. Please try again.');
        setLoading(false);
        return;
      }

      // 2. Create booking
      const bookingRes = await createBooking({ ...bookingData, phone: fullPhone });
      if (!bookingRes.success) {
        setError(bookingRes.message ?? 'Booking creation failed. Please try again.');
        setLoading(false);
        return;
      }

      toast.success('Booking confirmed! 🎉');
      onComplete(fullPhone, bookingRes.bookingRef);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Verification failed. Please try again.';
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto animate-slide-up">
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden">

        {/* ── Header ── */}
        <div className="bg-skynest-navy px-8 py-6">
          <p className="text-skynest-blue text-xs tracking-[0.2em] font-bold mb-1">STEP 4 OF 5</p>
          <div className="flex items-center gap-3">
            {mode === 'phone' ? (
              <HiPhone className="text-skynest-blue text-2xl flex-shrink-0" />
            ) : (
              <HiLockClosed className="text-skynest-blue text-2xl flex-shrink-0" />
            )}
            <div>
              <h2 className="text-xl font-bold text-white">
                {mode === 'phone' ? 'Phone Verification' : 'Enter Your OTP'}
              </h2>
              <p className="text-gray-400 text-xs mt-0.5">
                {mode === 'phone'
                  ? "We'll send an OTP to confirm your booking"
                  : `OTP sent to ${fullPhone}`}
              </p>
            </div>
          </div>
        </div>

        <div className="px-8 py-8">
          {/* Error banner */}
          {error && (
            <div className="mb-5 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* ── Phone Mode ── */}
          {mode === 'phone' && (
            <form onSubmit={handleSendOTP} className="space-y-5">
              <div>
                <label className="block text-xs font-bold text-skynest-navy tracking-[0.1em] mb-2 uppercase">
                  Mobile Number
                </label>
                <div className="flex">
                  <span className="flex items-center px-3 bg-skynest-blue-pale border border-r-0 border-gray-200 rounded-l-xl text-skynest-navy text-sm font-bold select-none">
                    +94
                  </span>
                  <input
                    type="tel"
                    value={phone}
                    onChange={e => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                    placeholder="7X XXX XXXX"
                    className="flex-1 px-4 py-3 border border-gray-200 rounded-r-xl text-skynest-navy text-lg font-semibold tracking-widest focus:outline-none focus:ring-2 focus:ring-skynest-blue/50 transition-all"
                    maxLength={10}
                    inputMode="numeric"
                  />
                </div>
                <p className="text-xs text-skynest-muted mt-1.5">
                  Enter your Sri Lankan mobile number (without country code)
                </p>
              </div>

              <button
                type="submit"
                disabled={loading || !phoneValid}
                className="w-full py-4 bg-skynest-blue text-white font-bold text-sm tracking-[0.15em] rounded-xl hover:bg-skynest-blue-hover transition-colors disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-skynest-blue/30"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Sending OTP...
                  </span>
                ) : (
                  'SEND OTP'
                )}
              </button>
            </form>
          )}

          {/* ── OTP Mode ── */}
          {mode === 'otp' && (
            <form onSubmit={handleVerifyOTP} className="space-y-5">
              <div>
                <label className="block text-xs font-bold text-skynest-navy tracking-[0.1em] mb-2 uppercase">
                  One-Time Password
                </label>
                <input
                  type="text"
                  value={otp}
                  onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="● ● ● ● ● ●"
                  className="w-full px-4 py-4 border-2 border-gray-200 rounded-xl text-skynest-navy focus:outline-none focus:border-skynest-blue transition-all otp-input"
                  maxLength={6}
                  inputMode="numeric"
                  autoComplete="one-time-code"
                />
                <p className="text-xs text-skynest-muted mt-1.5 text-center">
                  Check your SMS for the OTP code
                </p>
              </div>

              <button
                type="submit"
                disabled={loading || otp.length < 4}
                className="w-full py-4 bg-skynest-blue text-white font-bold text-sm tracking-[0.15em] rounded-xl hover:bg-skynest-blue-hover transition-colors disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-skynest-blue/30"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Verifying & Confirming...
                  </span>
                ) : (
                  'VERIFY & CONFIRM BOOKING'
                )}
              </button>

              {/* Resend */}
              <button
                type="button"
                onClick={() => handleSendOTP()}
                disabled={loading}
                className="w-full py-2 flex items-center justify-center gap-1.5 text-sm text-skynest-blue font-medium hover:text-skynest-blue-hover disabled:opacity-50 transition-colors"
              >
                <HiRefresh size={14} /> Resend OTP
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
