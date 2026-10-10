'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { HiOutlineChartBar, HiOutlineOfficeBuilding, HiOutlineViewGrid, HiOutlineCube, HiOutlineDocumentReport, HiOutlineClipboardList } from 'react-icons/hi';

const NAV_LINKS = [
  { name: 'Dashboard', href: '/admin', icon: HiOutlineChartBar },
  { name: 'Branch Management', href: '/admin/branches', icon: HiOutlineOfficeBuilding },
  { name: 'Room Management', href: '/admin/rooms', icon: HiOutlineViewGrid },
  { name: 'Bookings & Invoices', href: '/admin/bookings', icon: HiOutlineClipboardList },
  { name: 'Services & Addons', href: '/admin/services', icon: HiOutlineCube },
  { name: 'Financial Reports', href: '/admin/reports', icon: HiOutlineDocumentReport },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div 
      className="flex h-screen pt-16 overflow-hidden font-sans relative"
      style={{
        backgroundImage: 'url("https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80")', // Modern corporate/management vibe
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      
      {/* Background Overlay for the entire admin portal */}
      <div className="absolute inset-0 z-0 bg-white/30" />

      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col shadow-2xl relative z-10">
        <div className="p-6">
          <h1 className="text-2xl font-black tracking-widest text-sky-400">SKYNEST</h1>
          <p className="text-xs text-slate-400 font-semibold tracking-wider mt-1 uppercase">Management Portal</p>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link key={link.name} href={link.href}>
                <div className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 cursor-pointer ${isActive ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}>
                  <link.icon size={20} className={isActive ? 'text-white' : 'text-gray-400'} />
                  <span className="font-semibold text-sm tracking-wide">{link.name}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* User Profile Footer */}
        <div className="p-6 border-t border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center font-bold text-sky-400 border border-sky-400/30">
              AM
            </div>
            <div>
              <p className="text-sm font-bold text-white">Admin User</p>
              <p className="text-xs text-slate-400">System Administrator</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative z-0">
        {/* Header bar */}
        <header className="bg-white/70 backdrop-blur-md border-b border-white/30 h-16 flex items-center justify-between px-8 flex-shrink-0 z-10 shadow-sm">
          <h2 className="text-lg font-bold text-slate-800">
            {NAV_LINKS.find(l => l.href === pathname)?.name || 'Dashboard'}
          </h2>
          <div className="flex items-center gap-4">
            <div className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold border border-green-200 shadow-sm">
              System Status: Online
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </div>
      </main>

    </div>
  );
}
