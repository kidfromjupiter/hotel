'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { 
  HiOutlineSearch, 
  HiOutlineKey, 
  HiOutlineViewGrid, 
  HiOutlineUserGroup, 
  HiOutlineLogout,
  HiOutlineOfficeBuilding
} from 'react-icons/hi';
import { getAuthToken, getStoredUser, clearAuthSession } from '@/lib/api';
import type { StaffUser } from '@/lib/types';

const NAV_LINKS = [
  { name: 'Check-In (OTP)', href: '/receptionist', icon: HiOutlineKey },
  { name: 'Active Stays', href: '/receptionist/stays', icon: HiOutlineSearch },
  { name: 'Room Availability', href: '/receptionist/rooms', icon: HiOutlineViewGrid },
  { name: 'Guest Management', href: '/receptionist/guests', icon: HiOutlineUserGroup },
];

function getBranchLabel(branchId: number | null, role: string): { name: string; color: string } {
  if (role === 'admin') {
    return { name: 'All Branches (Admin)', color: 'bg-amber-500/10 text-amber-600 border-amber-500/20' };
  }
  switch (branchId) {
    case 1:
      return { name: 'Colombo Branch', color: 'bg-sky-500/10 text-sky-600 border-sky-500/20' };
    case 2:
      return { name: 'Kandy Branch', color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' };
    case 3:
      return { name: 'Galle Branch', color: 'bg-purple-500/10 text-purple-600 border-purple-500/20' };
    default:
      return { name: `Branch ${branchId}`, color: 'bg-gray-500/10 text-gray-600 border-gray-500/20' };
  }
}

function getInitials(name: string): string {
  if (!name) return 'ST';
  const parts = name.trim().split(' ');
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

export default function ReceptionistLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<StaffUser | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = getAuthToken();
    const storedUser = getStoredUser();

    if (!token || !storedUser) {
      router.push('/login');
    } else {
      setUser(storedUser);
      setChecking(false);
    }
  }, [router]);

  const handleLogout = () => {
    clearAuthSession();
    router.push('/login');
  };

  if (checking) {
    return (
      <div className="flex h-screen items-center justify-center bg-skynest-navy text-white">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-skynest-blue border-t-transparent rounded-full animate-spin" />
          <span className="text-xs text-gray-400 tracking-wider">Verifying staff session...</span>
        </div>
      </div>
    );
  }

  const branchInfo = getBranchLabel(user?.branch_id ?? null, user?.role ?? 'receptionist');

  return (
    <div 
      className="flex h-screen pt-16 overflow-hidden font-sans relative"
      style={{
        backgroundImage: 'url("https://images.unsplash.com/photo-1566073771259-6a8506099945?w=1920&q=80")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {/* Background Overlay */}
      <div className="absolute inset-0 z-0 bg-white/20" />

      {/* Sidebar Navigation */}
      <aside className="w-64 bg-skynest-navy text-white flex flex-col shadow-2xl relative z-10">
        <div className="p-6">
          <h1 className="text-2xl font-black tracking-widest text-skynest-blue">SKYNEST</h1>
          <div className="flex items-center gap-2 mt-2">
            <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${branchInfo.color}`}>
              {branchInfo.name}
            </span>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-2">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link key={link.name} href={link.href}>
                <div className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 cursor-pointer ${isActive ? 'bg-skynest-blue text-white shadow-lg shadow-skynest-blue/20' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}>
                  <link.icon size={20} className={isActive ? 'text-white' : 'text-gray-400'} />
                  <span className="font-semibold text-sm tracking-wide">{link.name}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* User Card & Logout Button */}
        <div className="p-4 border-t border-white/10 space-y-2">
          <div className="p-3 bg-white/5 rounded-xl flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-skynest-blue text-white flex items-center justify-center font-bold text-xs shadow-md">
              {getInitials(user?.full_name || 'Staff')}
            </div>
            <div className="overflow-hidden flex-1">
              <p className="text-xs font-bold text-white truncate">{user?.full_name}</p>
              <p className="text-[10px] text-gray-400 capitalize">{user?.role}</p>
            </div>
          </div>

          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-xl text-xs font-bold transition-colors cursor-pointer"
          >
            <HiOutlineLogout size={16} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative z-0">
        {/* Header bar */}
        <header className="bg-white/80 backdrop-blur-md border-b border-white/30 h-16 flex items-center justify-between px-8 flex-shrink-0 z-10 shadow-sm">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-bold text-skynest-navy">
              {NAV_LINKS.find(l => l.href === pathname)?.name || 'Dashboard'}
            </h2>
            <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${branchInfo.color}`}>
              {branchInfo.name}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-skynest-blue-pale text-skynest-blue flex items-center justify-center font-bold text-sm">
              {getInitials(user?.full_name || 'Staff')}
            </div>
            <div className="text-right">
              <span className="text-sm font-semibold text-gray-800 block leading-tight">{user?.full_name}</span>
              <span className="text-[10px] text-gray-500 block uppercase font-mono">{user?.username}</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </div>
      </main>

    </div>
  );
}
