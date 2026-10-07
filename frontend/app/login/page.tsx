'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { sendOTP, verifyOTP } from '@/lib/api';

export default function GuestLogin() {
  const router = useRouter();
  const [step, setStep] = useState<'PHONE' | 'OTP'>('PHONE');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.length < 9) {
      toast.error('Please enter a valid phone number');
      return;
    }

    setLoading(true);
    try {
      const res = await sendOTP(phone);
      toast.success(res.message || 'OTP sent to your phone', { duration: 6000 });
      setStep('OTP');
    } catch (err: any) {
      toast.error(err.message || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp || otp.length < 4) {
      toast.error('Please enter a valid OTP');
      return;
    }

    setLoading(true);
    try {
      const res = await verifyOTP(phone, otp);
      if (res.token) {
        localStorage.setItem('guest_token', res.token);
        toast.success('Successfully logged in');
        window.location.href = '/dashboard';
      }
    } catch (err: any) {
      toast.error(err.message || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-skynest-navy pt-24 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-xl shadow-2xl max-w-md w-full">
        <h1 className="text-2xl font-black text-skynest-navy tracking-widest text-center mb-2">GUEST LOGIN</h1>
        <p className="text-sm text-gray-500 text-center mb-8">Access your bookings and exclusive member benefits.</p>

        {step === 'PHONE' ? (
          <form onSubmit={handleSendOtp} className="space-y-6">
            <div>
              <label className="block text-xs font-bold text-gray-700 tracking-wider mb-2">PHONE NUMBER</label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+94 77 123 4567"
                className="w-full px-4 py-3 border border-gray-300 rounded-sm focus:outline-none focus:ring-2 focus:ring-skynest-blue focus:border-transparent transition-all"
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-skynest-blue hover:bg-skynest-blue-hover text-white font-bold py-3 px-4 rounded-sm transition-colors tracking-widest"
            >
              {loading ? 'SENDING...' : 'SEND OTP'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="space-y-6">
            <div>
              <label className="block text-xs font-bold text-gray-700 tracking-wider mb-2">ENTER OTP</label>
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="Enter the 6-digit code (demo: 789123)"
                className="w-full px-4 py-3 border border-gray-300 rounded-sm focus:outline-none focus:ring-2 focus:ring-skynest-blue focus:border-transparent text-center text-xl tracking-widest font-mono"
                disabled={loading}
                autoFocus
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-skynest-navy hover:bg-skynest-navy-light text-white font-bold py-3 px-4 rounded-sm transition-colors tracking-widest"
            >
              {loading ? 'VERIFYING...' : 'VERIFY & LOGIN'}
            </button>
            <button
              type="button"
              onClick={() => setStep('PHONE')}
              className="w-full text-xs text-skynest-blue hover:underline"
            >
              Change Phone Number
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
