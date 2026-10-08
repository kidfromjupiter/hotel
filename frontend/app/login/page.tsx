'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { 
  HiOutlineLockClosed, 
  HiOutlineUser, 
  HiOutlineShieldCheck, 
  HiOutlineEye, 
  HiOutlineEyeOff,
  HiOutlinePhone,
  HiOutlineKey,
  HiArrowRight,
  HiOutlineUserCircle
} from 'react-icons/hi';
import { loginStaff, sendOTP, verifyOTP } from '@/lib/api';

const DEMO_ACCOUNTS = [
  {
    role: 'Admin',
    name: 'System Admin',
    desc: 'Unrestricted access to Colombo, Kandy & Galle',
    username: 'admin',
    password: 'adminPassword123',
    badge: 'All Branches',
    badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  },
  {
    role: 'Receptionist',
    name: 'Colombo Desk',
    desc: 'Scoped to Colombo Branch (Branch 1)',
    username: 'rec_colombo',
    password: 'colomboPassword123',
    badge: 'Colombo',
    badgeColor: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
  },
  {
    role: 'Receptionist',
    name: 'Kandy Desk',
    desc: 'Scoped to Kandy Branch (Branch 2)',
    username: 'rec_kandy',
    password: 'kandyPassword123',
    badge: 'Kandy',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  },
  {
    role: 'Receptionist',
    name: 'Galle Desk',
    desc: 'Scoped to Galle Branch (Branch 3)',
    username: 'rec_galle',
    password: 'gallePassword123',
    badge: 'Galle',
    badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  },
];

function LoginFormContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = searchParams.get('type') === 'staff' ? 'staff' : 'guest';
  const [tab, setTab] = useState<'guest' | 'staff'>(initialTab);

  // Guest State
  const [guestStep, setGuestStep] = useState<'PHONE' | 'OTP'>('PHONE');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [guestLoading, setGuestLoading] = useState(false);

  // Staff State
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [staffLoading, setStaffLoading] = useState(false);
  const [staffError, setStaffError] = useState<string | null>(null);

  useEffect(() => {
    if (searchParams.get('type') === 'staff') {
      setTab('staff');
    }
  }, [searchParams]);

  // Guest Handlers
  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone || phone.length < 9) {
      toast.error('Please enter a valid phone number');
      return;
    }

    setGuestLoading(true);
    try {
      const res = await sendOTP(phone);
      toast.success(res.message || 'OTP sent to your phone', { duration: 6000 });
      setGuestStep('OTP');
    } catch (err: any) {
      toast.error(err.message || 'Failed to send OTP');
    } finally {
      setGuestLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp || otp.length < 4) {
      toast.error('Please enter a valid OTP');
      return;
    }

    setGuestLoading(true);
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
      setGuestLoading(false);
    }
  };

  // Staff Handlers
  const handleStaffSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStaffError(null);
    setStaffLoading(true);

    try {
      const response = await loginStaff(username.trim(), password);
      toast.success(`Welcome back, ${response.user.full_name}!`);
      if (response.user.role === 'admin') {
        router.push('/admin');
      } else {
        router.push('/receptionist');
      }
    } catch (err: any) {
      setStaffError(err?.message || 'Login failed. Please check your credentials.');
    } finally {
      setStaffLoading(false);
    }
  };

  const handleQuickFill = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setStaffError(null);
  };

  return (
    <div 
      className="min-h-screen pt-24 pb-16 px-4 flex flex-col justify-center items-center relative font-sans overflow-y-auto"
      style={{
        backgroundImage: 'url("https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=1920&q=80")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-skynest-navy/90 backdrop-blur-sm" />

      {/* Main card container */}
      <div className="relative z-10 w-full max-w-md">
        {/* Brand header */}
        <div className="text-center mb-6">
          <Link href="/" className="inline-block group">
            <h1 className="text-3xl font-black tracking-[0.2em] text-skynest-blue group-hover:text-skynest-blue-light transition-colors">
              SKYNEST
            </h1>
            <p className="text-[10px] text-skynest-blue-light/70 tracking-[0.4em] uppercase font-semibold mt-1">
              Hotels & Resorts Management
            </p>
          </Link>
        </div>

        {/* Tab switch */}
        <div className="flex bg-skynest-navy/90 border border-white/10 rounded-2xl p-1 mb-4 shadow-xl backdrop-blur-md">
          <button
            type="button"
            onClick={() => setTab('guest')}
            className={`flex-1 py-2.5 rounded-xl text-xs font-bold tracking-wide transition-all flex items-center justify-center gap-2 cursor-pointer ${
              tab === 'guest'
                ? 'bg-skynest-blue text-white shadow-md'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <HiOutlineUserCircle size={16} />
            Guest Access
          </button>
          <button
            type="button"
            onClick={() => setTab('staff')}
            className={`flex-1 py-2.5 rounded-xl text-xs font-bold tracking-wide transition-all flex items-center justify-center gap-2 cursor-pointer ${
              tab === 'staff'
                ? 'bg-skynest-blue text-white shadow-md'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <HiOutlineShieldCheck size={16} />
            Staff & Admin
          </button>
        </div>

        {/* Card Body */}
        <div className="bg-skynest-navy-light/95 border border-white/10 rounded-2xl shadow-2xl p-6 sm:p-7 backdrop-blur-xl">
          {tab === 'guest' ? (
            /* ──────── GUEST LOGIN ──────── */
            <div>
              <div className="flex items-center justify-between mb-1">
                <h2 className="text-xl font-bold text-white">Guest Sign In</h2>
                <span className="text-[10px] px-2 py-0.5 rounded border border-skynest-blue/30 text-skynest-blue-light font-mono">
                  OTP VERIFIED
                </span>
              </div>
              <p className="text-xs text-gray-400 mb-6">
                Access your bookings, loyalty discounts, and exclusive stays.
              </p>

              {guestStep === 'PHONE' ? (
                <form onSubmit={handleSendOtp} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
                      Phone Number
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                        <HiOutlinePhone size={18} />
                      </div>
                      <input
                        type="tel"
                        required
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="+94 77 123 4567"
                        disabled={guestLoading}
                        className="w-full pl-10 pr-4 py-2.5 bg-skynest-navy/80 border border-white/10 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-skynest-blue focus:border-transparent transition-all"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={guestLoading}
                    className="w-full mt-2 py-3 px-4 bg-skynest-blue hover:bg-skynest-blue-hover text-white rounded-xl text-sm font-bold tracking-wide transition-all shadow-lg shadow-skynest-blue/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  >
                    {guestLoading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>Sending OTP...</span>
                      </>
                    ) : (
                      <>
                        <span>Send Verification Code</span>
                        <HiArrowRight size={16} />
                      </>
                    )}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleVerifyOtp} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
                      Enter 6-Digit OTP
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                        <HiOutlineKey size={18} />
                      </div>
                      <input
                        type="text"
                        required
                        value={otp}
                        onChange={(e) => setOtp(e.target.value)}
                        placeholder="789123"
                        autoFocus
                        disabled={guestLoading}
                        className="w-full pl-10 pr-4 py-2.5 bg-skynest-navy/80 border border-white/10 rounded-xl text-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-skynest-blue focus:border-transparent text-center tracking-widest font-mono"
                      />
                    </div>
                    <p className="text-[11px] text-gray-400 mt-1.5 text-center">
                      Demo code: <span className="font-mono text-skynest-blue-light font-bold">789123</span>
                    </p>
                  </div>

                  <button
                    type="submit"
                    disabled={guestLoading}
                    className="w-full mt-2 py-3 px-4 bg-skynest-blue hover:bg-skynest-blue-hover text-white rounded-xl text-sm font-bold tracking-wide transition-all shadow-lg shadow-skynest-blue/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  >
                    {guestLoading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>Verifying Code...</span>
                      </>
                    ) : (
                      <>
                        <span>Verify & Sign In</span>
                        <HiArrowRight size={16} />
                      </>
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={() => setGuestStep('PHONE')}
                    className="w-full text-xs text-gray-400 hover:text-white text-center transition-colors cursor-pointer pt-1"
                  >
                    Change Phone Number
                  </button>
                </form>
              )}
            </div>
          ) : (
            /* ──────── STAFF LOGIN ──────── */
            <div>
              <div className="flex items-center justify-between mb-1">
                <h2 className="text-xl font-bold text-white">Staff Sign In</h2>
                <span className="text-[10px] px-2 py-0.5 rounded border border-amber-500/30 text-amber-400 font-mono">
                  ROLE SCOPED
                </span>
              </div>
              <p className="text-xs text-gray-400 mb-5">
                Enter your staff credentials to access reception, billing, and reservations.
              </p>

              {staffError && (
                <div className="mb-5 p-3.5 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-xs flex items-start gap-2.5">
                  <span className="font-bold">Error:</span>
                  <span>{staffError}</span>
                </div>
              )}

              <form onSubmit={handleStaffSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
                    Username
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                      <HiOutlineUser size={18} />
                    </div>
                    <input
                      type="text"
                      required
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="e.g. admin or rec_colombo"
                      className="w-full pl-10 pr-4 py-2.5 bg-skynest-navy/80 border border-white/10 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-skynest-blue focus:border-transparent transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                      <HiOutlineLockClosed size={18} />
                    </div>
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      className="w-full pl-10 pr-10 py-2.5 bg-skynest-navy/80 border border-white/10 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-skynest-blue focus:border-transparent transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-white transition-colors"
                    >
                      {showPassword ? <HiOutlineEyeOff size={18} /> : <HiOutlineEye size={18} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={staffLoading}
                  className="w-full mt-2 py-3 px-4 bg-skynest-blue hover:bg-skynest-blue-hover text-white rounded-xl text-sm font-bold tracking-wide transition-all shadow-lg shadow-skynest-blue/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                >
                  {staffLoading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Verifying Credentials...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign In</span>
                      <HiArrowRight size={16} />
                    </>
                  )}
                </button>
              </form>

              {/* Quick Fill Demo Section */}
              <div className="mt-8 pt-6 border-t border-white/10">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                    Demo Quick Fill
                  </span>
                  <span className="text-[10px] text-skynest-blue-light/60">Click to autofill</span>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {DEMO_ACCOUNTS.map((acc) => (
                    <button
                      key={acc.username}
                      type="button"
                      onClick={() => handleQuickFill(acc.username, acc.password)}
                      className="p-2.5 rounded-xl bg-skynest-navy/60 hover:bg-skynest-navy border border-white/5 hover:border-skynest-blue/40 text-left transition-all group"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white group-hover:text-skynest-blue transition-colors">
                          {acc.name}
                        </span>
                        <span className={`text-[9px] px-1.5 py-0.5 rounded border ${acc.badgeColor} font-semibold`}>
                          {acc.badge}
                        </span>
                      </div>
                      <div className="text-[10px] text-gray-500 mt-1 font-mono">
                        {acc.username}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer links */}
        <div className="text-center mt-6 text-xs text-gray-400">
          <Link href="/" className="hover:text-white transition-colors">
            ← Return to Guest Booking Site
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-skynest-navy flex items-center justify-center">
        <div className="w-8 h-8 border-3 border-skynest-blue border-t-transparent rounded-full animate-spin" />
      </div>
    }>
      <LoginFormContent />
    </Suspense>
  );
}
