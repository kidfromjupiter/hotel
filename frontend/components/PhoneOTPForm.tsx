'use client';

import { useState } from 'react';
import { HiPhone, HiArrowLeft, HiArrowRight, HiShieldCheck, HiRefresh } from 'react-icons/hi';
import { sendOTP, verifyOTP, createBooking } from '@/lib/api';
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
  const [stage, setStage] = useState<'phone' | 'otp'>('phone');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fullPhone = toE164(phone);
  const phoneDigits = phone.replace(/\D/g, '');
  const phoneValid = phoneDigits.length >= 9;
  const otpValid = otp.trim().length === 6;

  // ── Step 1: Send OTP ─────────────────────────
  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!phoneValid) {
      setError('Please enter a valid 9-digit Sri Lankan phone number (e.g. 771234567).');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await sendOTP(fullPhone);
      if (res.success) {
        toast.success(res.message || 'OTP sent successfully!');
        setStage('otp');
      } else {
        setError(res.message || 'Failed to send OTP. Please try again.');
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to send OTP SMS.';
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  // ── Step 2: Verify OTP & Create Booking ───────
  const handleVerifyAndBook = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!otpValid) {
      setError('Please enter the 6-digit OTP code received via SMS.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // 1. Verify OTP with backend
      const verifyRes = await verifyOTP(fullPhone, otp.trim());
      if (!verifyRes.success) {
        setError(verifyRes.message || 'Invalid or expired OTP');
        setLoading(false);
        return;
      }

      // 2. Once verified, finalize the booking
      const bookingRes = await createBooking({ ...bookingData, phone: fullPhone });
      if (!bookingRes.success) {
        setError(bookingRes.message || 'Booking failed. Please try again.');
        setLoading(false);
        return;
      }

      toast.success('Phone verified & booking confirmed! 🎉');
      onComplete(fullPhone, bookingRes.bookingRef);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Invalid or expired OTP.';
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
            {stage === 'phone' ? (
              <HiPhone className="text-skynest-blue text-2xl flex-shrink-0" />
            ) : (
              <HiShieldCheck className="text-skynest-blue text-2xl flex-shrink-0" />
            )}
            <div>
              <h2 className="text-xl font-bold text-white">
                {stage === 'phone' ? 'Phone Verification' : 'Enter Verification Code'}
              </h2>
              <p className="text-gray-400 text-xs mt-0.5">
                {stage === 'phone'
                  ? 'We will send a one-time verification code via SMS'
                  : `Code sent to ${fullPhone}`}
              </p>
            </div>
          </div>
        </div>

        <div className="px-8 py-8">

          {/* Quick Notice */}
          <div className="mb-6 bg-skynest-blue-pale border border-skynest-blue/20 rounded-xl p-4">
            <p className="text-xs font-bold text-skynest-navy tracking-wide mb-1">
              {stage === 'phone' ? 'SMS AUTHENTICATION' : '5-MINUTE VALIDITY'}
            </p>
            <p className="text-xs text-skynest-muted leading-relaxed">
              {stage === 'phone'
                ? 'To ensure secure reservations, SkyNest verifies your mobile number before confirming your booking.'
                : 'Please check your phone messages for the 6-digit verification code to complete your booking.'}
            </p>
          </div>

          {/* Error banner */}
          {error && (
            <div className="mb-5 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              {error}
            </div>
          )}

          {stage === 'phone' ? (
            /* ── Phone Number Input Form ── */
            <form onSubmit={handleSendOTP} className="space-y-6">
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
                      <span>Sending OTP...</span>
                    </>
                  ) : (
                    <>
                      <span>Send Verification Code</span>
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
          ) : (
            /* ── OTP Code Verification Form ── */
            <form onSubmit={handleVerifyAndBook} className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-xs font-bold text-skynest-navy tracking-[0.1em] uppercase">
                    6-Digit Verification Code
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      setStage('phone');
                      setOtp('');
                      setError(null);
                    }}
                    className="text-xs text-skynest-blue hover:underline font-semibold"
                  >
                    Change Number
                  </button>
                </div>

                <input
                  type="text"
                  value={otp}
                  onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="• • • • • •"
                  className="w-full text-center tracking-[0.5em] px-4 py-3 border border-gray-200 rounded-xl text-skynest-navy text-2xl font-black focus:outline-none focus:ring-2 focus:ring-skynest-blue/50 transition-all"
                  maxLength={6}
                  inputMode="numeric"
                  autoFocus
                />
                <p className="text-xs text-skynest-muted mt-1.5 text-center">
                  Check your SMS inbox for the 6-digit OTP code
                </p>
              </div>

              <div className="space-y-3 pt-2">
                <button
                  type="submit"
                  disabled={loading || !otpValid}
                  className="w-full py-4 bg-skynest-blue text-white font-bold text-sm tracking-[0.15em] rounded-xl hover:bg-skynest-blue-hover transition-colors disabled:opacity-60 disabled:cursor-not-allowed shadow-lg shadow-skynest-blue/30 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Verifying &amp; Booking...</span>
                    </>
                  ) : (
                    <>
                      <span>Verify &amp; Confirm Booking</span>
                      <HiShieldCheck size={18} />
                    </>
                  )}
                </button>

                <div className="flex items-center justify-between pt-1 text-xs">
                  <button
                    type="button"
                    onClick={() => {
                      setStage('phone');
                      setOtp('');
                    }}
                    disabled={loading}
                    className="text-gray-500 hover:text-gray-700 flex items-center gap-1 font-medium"
                  >
                    <HiArrowLeft size={14} />
                    <span>Back</span>
                  </button>

                  <button
                    type="button"
                    onClick={async () => {
                      setLoading(true);
                      setError(null);
                      try {
                        const res = await sendOTP(fullPhone);
                        toast.success(res.message || 'New OTP sent!');
                      } catch (err) {
                        const msg = err instanceof Error ? err.message : 'Failed to resend OTP.';
                        setError(msg);
                      } finally {
                        setLoading(false);
                      }
                    }}
                    disabled={loading}
                    className="text-skynest-blue hover:text-skynest-blue-hover font-semibold flex items-center gap-1"
                  >
                    <HiRefresh size={14} />
                    <span>Resend Code</span>
                  </button>
                </div>
              </div>
            </form>
          )}

        </div>
      </div>
    </div>
  );
}

