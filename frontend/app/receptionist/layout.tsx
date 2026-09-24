'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { HiOutlineSearch, HiOutlineKey, HiOutlineViewGrid, HiOutlineUserGroup, HiOutlineChatAlt2 } from 'react-icons/hi';

const NAV_LINKS = [
  { name: 'Check-In (OTP)', href: '/receptionist', icon: HiOutlineKey },
  { name: 'Active Stays', href: '/receptionist/stays', icon: HiOutlineSearch },
  { name: 'Room Availability', href: '/receptionist/rooms', icon: HiOutlineViewGrid },
  { name: 'Guest Management', href: '/receptionist/guests', icon: HiOutlineUserGroup },
];

export default function ReceptionistLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden font-sans">
      
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-skynest-navy text-white flex flex-col shadow-2xl">
        <div className="p-6">
          <h1 className="text-2xl font-black tracking-widest text-skynest-blue">SKYNEST</h1>
          <p className="text-xs text-skynest-blue-light font-semibold tracking-wider mt-1 uppercase">Reception Desk</p>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
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

        {/* Contact Admin Button */}
        <div className="p-6 border-t border-white/10">
          <button className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 text-white rounded-xl text-sm font-bold transition-colors">
            <HiOutlineChatAlt2 size={18} className="text-skynest-blue" />
            Contact Admin
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header bar */}
        <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-8 flex-shrink-0 z-10">
          <h2 className="text-lg font-bold text-skynest-navy">
            {NAV_LINKS.find(l => l.href === pathname)?.name || 'Dashboard'}
          </h2>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-skynest-blue-pale text-skynest-blue flex items-center justify-center font-bold text-sm">
              RD
            </div>
            <span className="text-sm font-semibold text-gray-600">Receptionist Desk 1</span>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-8 bg-gray-50">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </div>
      </main>

    </div>
  );
}
