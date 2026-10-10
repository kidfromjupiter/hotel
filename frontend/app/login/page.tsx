'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  HiOutlineLockClosed, 
  HiOutlineUser, 
  HiOutlineShieldCheck, 
  HiOutlineEye, 
  HiOutlineEyeOff,
  HiOutlineOfficeBuilding,
  HiArrowRight
} from 'react-icons/hi';
import { loginStaff } from '@/lib/api';

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

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await loginStaff(username.trim(), password);
      // Successfully authenticated
      router.push('/receptionist');
    } catch (err: any) {
      setError(err?.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setError(null);
  };

  return (
    <div 
      className="min-h-screen pt-28 pb-16 px-4 flex flex-col justify-center items-center relative font-sans overflow-y-auto"
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
          <div className="mt-3 inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs text-gray-300 shadow-md">
            <HiOutlineShieldCheck className="text-skynest-blue" size={16} />
            <span className="font-semibold tracking-wide">Staff & Admin Portal</span>
          </div>
        </div>

        {/* Login form card */}
        <div className="bg-skynest-navy-light/95 border border-white/10 rounded-2xl shadow-2xl p-6 sm:p-7 backdrop-blur-xl">
          <h2 className="text-xl font-bold text-white mb-1">Sign In</h2>
          <p className="text-xs text-gray-400 mb-5">
            Enter your staff credentials to access reception, billing, and reservations.
          </p>

          {error && (
            <div className="mb-5 p-3.5 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-xs flex items-start gap-2.5">
              <span className="font-bold">Error:</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
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
              disabled={loading}
              className="w-full mt-2 py-3 px-4 bg-skynest-blue hover:bg-skynest-blue-hover text-white rounded-xl text-sm font-bold tracking-wide transition-all shadow-lg shadow-skynest-blue/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {loading ? (
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
