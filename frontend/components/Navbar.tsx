'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { HiMenu, HiX } from 'react-icons/hi';

const NAV_LINKS = [
  { label: 'HOME', href: '/' },
  { label: 'ACCOMMODATIONS', href: '/#accommodations' },
  { label: 'OUR SPA', href: '/#spa' },
  { label: 'GALLERY', href: '/#gallery' },
  { label: 'OFFERS', href: '/#offers' },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();
  const isBookingPage = pathname.startsWith('/booking');

  return (
    <nav className="fixed top-0 inset-x-0 z-50 bg-skynest-navy/95 backdrop-blur-sm border-b border-skynest-navy-light">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* ── Logo ── */}
          <Link href="/" className="group flex-shrink-0">
            <div className="flex flex-col leading-none">
              <span className="text-[22px] font-black text-skynest-blue tracking-[0.15em] group-hover:text-skynest-blue-light transition-colors">
                SKYNEST
              </span>
              <span className="text-[7px] text-skynest-blue-light/70 tracking-[0.4em] mt-0.5">
                LUXURY HOTELS
              </span>
            </div>
          </Link>

          {/* ── Desktop nav links ── */}
          <div className="hidden md:flex items-center gap-7">
            {NAV_LINKS.map(link => (
              <Link
                key={link.label}
                href={link.href}
                className="text-[10px] tracking-[0.15em] text-gray-400 hover:text-white transition-colors font-semibold"
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* ── CTA + Mobile toggle ── */}
          <div className="flex items-center gap-3">
            <Link
              href="/booking"
              className={`hidden sm:inline-flex items-center gap-1.5 px-5 py-2 text-[11px] font-bold tracking-[0.15em] rounded-sm transition-all duration-200 ${
                isBookingPage
                  ? 'bg-skynest-blue-light text-skynest-navy'
                  : 'bg-skynest-blue text-white hover:bg-skynest-blue-hover shadow-lg shadow-skynest-blue/20'
              }`}
            >
              BOOK NOW
            </Link>
            <button
              className="md:hidden text-gray-300 hover:text-white transition-colors p-1"
              onClick={() => setMobileOpen(v => !v)}
              aria-label="Toggle menu"
            >
              {mobileOpen ? <HiX size={22} /> : <HiMenu size={22} />}
            </button>
          </div>
        </div>
      </div>

      {/* ── Mobile drawer ── */}
      {mobileOpen && (
        <div className="md:hidden bg-skynest-navy-light border-t border-skynest-navy px-5 py-4 space-y-1 animate-fade-in">
          {NAV_LINKS.map(link => (
            <Link
              key={link.label}
              href={link.href}
              className="block py-2.5 text-[11px] tracking-[0.15em] text-gray-400 hover:text-white font-semibold"
              onClick={() => setMobileOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <div className="pt-3">
            <Link
              href="/booking"
              className="block text-center py-3 bg-skynest-blue text-white text-[11px] font-bold tracking-[0.15em] rounded-sm hover:bg-skynest-blue-hover transition-colors"
              onClick={() => setMobileOpen(false)}
            >
              BOOK NOW
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
