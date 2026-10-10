'use client';

import { useState } from 'react';
import { HiArrowLeft, HiArrowRight, HiShieldCheck, HiRefresh } from 'react-icons/hi';
import { sendOTP, verifyOTP, createBooking } from '@/lib/api';
import type { CreateBookingPayload } from '@/lib/types';
import toast from 'react-hot-toast';

interface PhoneConfirmFormProps {
  bookingData: Omit<CreateBookingPayload, 'phone'>;
  onBack: () => void;
  onComplete: (
    phone: string,
    bookingRef: string,
    details?: {
      firstName?: string;
      lastName?: string;
      email?: string;
      specialRequests?: string;
      nationalId?: string;
    }
  ) => void;
}

/** Normalize input to +94XXXXXXXXX format */
function toE164(local: string): string {
  const digits = local.replace(/\D/g, '');
  if (digits.startsWith('94')) {
    return `+${digits}`;
  }
  const stripped = digits.startsWith('0') ? digits.slice(1) : digits;
  return `+94${stripped}`;
}

export default function PhoneOTPForm({ bookingData, onBack, onComplete }: PhoneConfirmFormProps) {
  const [stage, setStage] = useState<'contact' | 'otp'>('contact');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [nationalId, setNationalId] = useState('');
  const [specialRequests, setSpecialRequests] = useState('');

  const [otp, setOtp] = useState('');
  const [demoCodeHint, setDemoCodeHint] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fullPhone = toE164(phone);
  const phoneDigits = phone.replace(/\D/g, '');
  const isPhoneValid = phoneDigits.length >= 9;
  const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
  const isContactValid = firstName.trim().length > 0 && lastName.trim().length > 0 && isEmailValid && isPhoneValid;
  const otpValid = otp.trim().length === 6;

  // ── Step 1: Validate contact details & Send OTP ──
  const handleProceedToOTP = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!firstName.trim()) {
      setError('Please provide the primary guest first name.');
      return;
    }
    if (!lastName.trim()) {
      setError('Please provide the primary guest last name.');
      return;
    }
    if (!isEmailValid) {
      setError('Please provide a valid email address (e.g. name@example.com).');
      return;
    }
    if (!isPhoneValid) {
      setError('Please enter a valid phone number with at least 9 digits (e.g. +94 77 123 4567).');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await sendOTP(fullPhone);
      if (res.success) {
        toast.success(res.message || 'OTP sent successfully!');
        if (res.message && res.message.includes('Demo Code:')) {
          const match = res.message.match(/Demo Code:\s*(\d+)/);
          if (match) setDemoCodeHint(match[1]);
        }
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

  // ── Step 2: Verify OTP & Create Booking ───────────
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

      if (verifyRes.has_membership && localStorage.getItem('guest_token')) {
        toast.success('Phone verified! Membership discount applied! 🎉');
      } else {
        toast.success('Phone verified successfully!');
      }

      // 2. Once verified, finalize the booking with full contact details
      const bookingPayload: CreateBookingPayload = {
        ...bookingData,
        phone: fullPhone,
        firstName: firstName.trim(),
        lastName: lastName.trim(),
        name: `${firstName.trim()} ${lastName.trim()}`,
        email: email.trim(),
        nationalId: nationalId.trim() || undefined,
        specialRequests: specialRequests.trim() || undefined,
      };

      const bookingRes = await createBooking(bookingPayload);
      if (!bookingRes.success) {
        setError(bookingRes.message || 'Booking failed. Please try again.');
        setLoading(false);
        return;
      }

      toast.success('Booking confirmed & saved to database! 🎉');
      onComplete(fullPhone, bookingRes.bookingRef, {
        firstName: firstName.trim(),
        lastName: lastName.trim(),
        email: email.trim(),
        specialRequests: specialRequests.trim() || undefined,
        nationalId: nationalId.trim() || undefined,
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Invalid or expired OTP.';
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto animate-slide-up">
      {stage === 'contact' ? (
        /* ── Figure 6: PRIMARY GUEST CONTACT INFORMATION ── */
        <div className="bg-white rounded-xl border border-gray-200/90 shadow-sm p-6 sm:p-10">
          {/* Header */}
          <div className="border-b border-gray-100 pb-5 mb-8">
            <div className="flex items-center gap-2.5">
              <span className="bg-[#0f1d33] text-white text-xs font-black px-2 py-0.5 rounded-sm tracking-wider">
                02
              </span>
              <h2 className="font-serif text-[#0f1d33] text-base sm:text-lg font-bold tracking-[0.16em] uppercase">
                PRIMARY GUEST CONTACT INFORMATION
              </h2>
            </div>
            <p className="text-xs text-gray-500 mt-2 font-normal tracking-wide">
              The primary contact person responsible for this single reservation across all 1 room.
            </p>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mb-6 px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleProceedToOTP} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-6">
              {/* FIRST NAME */}
              <div>
                <label className="block text-[11px] font-bold text-gray-600 tracking-[0.12em] uppercase mb-2">
                  FIRST NAME *
                </label>
                <input
                  type="text"
                  value={firstName}
                  onChange={e => setFirstName(e.target.value)}
                  placeholder="First Name"
                  required
                  className="w-full px-4 py-3 bg-[#fdfdfc] border border-gray-200 rounded-md text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#0f1d33] focus:bg-white transition"
                />
              </div>

              {/* LAST NAME */}
              <div>
                <label className="block text-[11px] font-bold text-gray-600 tracking-[0.12em] uppercase mb-2">
                  LAST NAME *
                </label>
                <input
                  type="text"
                  value={lastName}
                  onChange={e => setLastName(e.target.value)}
                  placeholder="Last Name"
                  required
                  className="w-full px-4 py-3 bg-[#fdfdfc] border border-gray-200 rounded-md text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#0f1d33] focus:bg-white transition"
                />
              </div>

              {/* EMAIL ADDRESS */}
              <div>
                <label className="block text-[11px] font-bold text-gray-600 tracking-[0.12em] uppercase mb-2">
                  EMAIL ADDRESS *
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                  className="w-full px-4 py-3 bg-[#fdfdfc] border border-gray-200 rounded-md text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#0f1d33] focus:bg-white transition"
                />
              </div>

              {/* PHONE NUMBER */}
              <div>
                <label className="block text-[11px] font-bold text-gray-600 tracking-[0.12em] uppercase mb-2">
                  PHONE NUMBER *
                </label>
                <input
                  type="tel"
                  value={phone}
                  onChange={e => setPhone(e.target.value)}
                  placeholder="+94 77 123 4567"
                  required
                  className="w-full px-4 py-3 bg-[#fdfdfc] border border-gray-200 rounded-md text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#0f1d33] focus:bg-white transition"
                />
              </div>

              {/* NATIONAL ID / PASSPORT (OPTIONAL) */}
              <div className="md:col-span-2">
                <label className="block text-[11px] font-bold text-gray-600 tracking-[0.12em] uppercase mb-2">
                  NATIONAL ID / PASSPORT NUMBER (OPTIONAL)
                </label>
                <input
                  type="text"
                  value={nationalId}
                  onChange={e => setNationalId(e.target.value)}
                  placeholder="e.g. 200012345678 or N1234567"
                  className="w-full px-4 py-3 bg-[#fdfdfc] border border-gray-200 rounded-md text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#0f1d33] focus:bg-white transition"
                />
              </div>

              {/* SPECIAL REQUESTS */}
              <div className="md:col-span-2">
                <label className="block text-[11px] font-bold text-gray-600 tracking-[0.12em] uppercase mb-2">
                  SPECIAL REQUESTS / DIETARY REQUIREMENTS
                </label>
                <textarea
                  value={specialRequests}
                  onChange={e => setSpecialRequests(e.target.value)}
                  placeholder="Connecting rooms, quiet floor, dietary restrictions, airport pickup..."
                  rows={3}
                  className="w-full px-4 py-3 bg-[#fdfdfc] border border-gray-200 rounded-md text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#0f1d33] focus:bg-white transition resize-none"
                />
              </div>
            </div>

            {/* Bottom Form Actions */}
            <div className="pt-6 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-4">
              <button
                type="button"
                onClick={onBack}
                disabled={loading}
                className="w-full sm:w-auto px-6 py-3 border border-gray-300 text-gray-700 font-bold text-xs uppercase tracking-wider rounded-lg hover:bg-gray-50 transition flex items-center justify-center gap-2"
              >
                <HiArrowLeft size={16} />
                <span>Back to Summary</span>
              </button>

              <button
                type="submit"
                disabled={loading || !isContactValid}
                className="w-full sm:w-auto px-8 py-3.5 bg-[#0f1d33] hover:bg-[#1a3154] text-white font-bold text-xs uppercase tracking-[0.15em] rounded-lg transition shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Sending Verification Code...</span>
                  </>
                ) : (
                  <>
                    <span>Proceed to Verification</span>
                    <HiArrowRight size={16} />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      ) : (
        /* ── Stage 2: OTP Verification Card ── */
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden max-w-lg mx-auto">
          <div className="bg-[#0f1d33] px-8 py-6 text-white">
            <p className="text-sky-300 text-xs tracking-[0.2em] font-bold mb-1 uppercase">STEP 4 OF 5</p>
            <div className="flex items-center gap-3">
              <HiShieldCheck className="text-sky-400 text-2xl flex-shrink-0" />
              <div>
                <h2 className="text-xl font-bold">Enter Verification Code</h2>
                <p className="text-gray-300 text-xs mt-0.5">
                  Code sent via SMS to <span className="font-semibold text-white">{fullPhone}</span>
                </p>
              </div>
            </div>
          </div>

          <div className="p-8">
            <div className="mb-6 bg-sky-50 border border-sky-200 rounded-xl p-4">
              <p className="text-xs font-bold text-[#0f1d33] tracking-wide mb-1">
                GUEST: {firstName} {lastName}
              </p>
              <p className="text-xs text-gray-600 leading-relaxed">
                Confirmation voucher will be issued for <strong>{email}</strong> upon SMS phone verification.
              </p>
              {demoCodeHint && (
                <p className="text-xs font-mono font-bold text-sky-800 mt-2 bg-sky-100 px-2 py-1 rounded inline-block">
                  Demo SMS Code: {demoCodeHint}
                </p>
              )}
            </div>

            {error && (
              <div className="mb-5 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleVerifyAndBook} className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-xs font-bold text-[#0f1d33] tracking-[0.1em] uppercase">
                    6-Digit Verification Code
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      setStage('contact');
                      setOtp('');
                      setError(null);
                    }}
                    className="text-xs text-sky-600 hover:underline font-semibold"
                  >
                    Edit Contact Details
                  </button>
                </div>

                <input
                  type="text"
                  value={otp}
                  onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="• • • • • •"
                  className="w-full text-center tracking-[0.5em] px-4 py-3 border border-gray-300 rounded-xl text-[#0f1d33] text-2xl font-black focus:outline-none focus:ring-2 focus:ring-sky-500/50 transition-all"
                  maxLength={6}
                  inputMode="numeric"
                  autoFocus
                />
                <p className="text-xs text-gray-500 mt-1.5 text-center">
                  Check your phone messages for the 6-digit OTP code (or use demo code: 123456)
                </p>
              </div>

              <div className="space-y-3 pt-2">
                <button
                  type="submit"
                  disabled={loading || !otpValid}
                  className="w-full py-4 bg-[#0f1d33] hover:bg-[#1a3154] text-white font-bold text-sm tracking-[0.15em] rounded-xl transition disabled:opacity-60 disabled:cursor-not-allowed shadow-lg flex items-center justify-center gap-2"
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
                      setStage('contact');
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
                        if (res.message && res.message.includes('Demo Code:')) {
                          const match = res.message.match(/Demo Code:\s*(\d+)/);
                          if (match) setDemoCodeHint(match[1]);
                        }
                      } catch (err) {
                        const msg = err instanceof Error ? err.message : 'Failed to resend OTP.';
                        setError(msg);
                      } finally {
                        setLoading(false);
                      }
                    }}
                    disabled={loading}
                    className="text-sky-600 hover:text-sky-700 font-semibold flex items-center gap-1"
                  >
                    <HiRefresh size={14} />
                    <span>Resend Code</span>
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

