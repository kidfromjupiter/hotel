'use client';

import { useState } from 'react';
import { HiPhone, HiArrowLeft, HiArrowRight } from 'react-icons/hi';
import { createBooking } from '@/lib/api';
import type { CreateBookingPayload } from '@/lib/types';
import toast from 'react-hot-toast';

interface PhoneConfirmFormProps {
  bookingData: Omit<CreateBookingPayload, 'phone'>;
  onBack: () => void;
  onComplete: (phone: string, bookingRef: string) => void;
}

/** Strip leading 0 and format as +94XXXXXXXXX */
function toE164(local: string): string {
  const digits = local.replace(/\D/g, '');
  const stripped = digits.startsWith('0') ? digits.slice(1) : digits;
  return `+94${stripped}`;
}

export default function PhoneOTPForm({ bookingData, onBack, onComplete }: PhoneConfirmFormProps) {
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fullPhone = toE164(phone);
  const phoneDigits = phone.replace(/\D/g, '');
  const phoneValid = phoneDigits.length >= 9;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!phoneValid) {
      setError('Please enter a valid 9-digit Sri Lankan phone number (e.g. 771234567).');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Send all booking details + phone number to backend
      const result = await createBooking({ ...bookingData, phone: fullPhone });

      if (!result.success) {
        setError(result.message ?? 'Booking failed. Please try again.');
        setLoading(false);
        return;
      }

      toast.success('Booking confirmed! OTP sent to your phone 🎉');
      onComplete(fullPhone, result.bookingRef);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Something went wrong. Please try again.';
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
          <p className="text-skynest-blue text-xs tracking-[0.2em] font-bold mb-1 uppercase">STEP 4 OF 5</p>
          <div className="flex items-center gap-3">
            <HiPhone className="text-skynest-blue text-2xl flex-shrink-0" />
            <div>
              <h2 className="text-xl font-bold text-white">Contact Phone Number</h2>
              <p className="text-gray-400 text-xs mt-0.5">
                We will send your check-in OTP code to this mobile number
              </p>
            </div>
          </div>
        </div>

        <div className="px-8 py-8">

          {/* Quick Notice */}
          <div className="mb-6 bg-skynest-blue-pale border border-skynest-blue/20 rounded-xl p-4">
            <p className="text-xs font-bold text-skynest-navy tracking-wide mb-1">IMPORTANT NOTICE</p>
            <p className="text-xs text-skynest-muted leading-relaxed">
              When you submit, an OTP verification code will be dispatched to your mobile number. Please keep that SMS safe to show to the hotel receptionist when you check in.
            </p>
          </div>

          {/* Error banner */}
          {error && (
            <div className="mb-5 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
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
                  autoFocus
                />
              </div>
              <p className="text-xs text-skynest-muted mt-1.5">
                Enter 9 digits without leading 0 (e.g., 77 123 4567)
              </p>
            </div>

            <div className="space-y-3 pt-2">
              <button
                type="submit"
                disabled={loading || !phoneValid}
                className="w-full py-4 bg-skynest-blue text-white font-bold text-sm tracking-[0.15em] rounded-xl hover:bg-skynest-blue-hover transition-colors disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-skynest-blue/30 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Sending to Backend...</span>
                  </>
                ) : (
                  <>
                    <span>Continue &amp; Place Booking</span>
                    <HiArrowRight size={16} />
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={onBack}
                disabled={loading}
                className="w-full py-3 border border-gray-200 text-skynest-navy font-bold text-sm rounded-xl hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
              >
                <HiArrowLeft size={16} />
                <span>Go Back to Summary</span>
              </button>
            </div>

          </form>
        </div>
      </div>
    </div>
  );
}
