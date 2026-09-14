import Image from 'next/image';
import Link from 'next/link';
import { HiArrowRight } from 'react-icons/hi';

export default function LandingPage() {
  return (
    <>
      {/* ════════════════════════════════════════════
          HERO — Full-viewport
      ════════════════════════════════════════════ */}
      <section className="relative h-screen">
        {/* Background image */}
        <Image
          src="https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=1920&q=80"
          alt="SkyNest luxury hotel room"
          fill
          priority
          className="object-cover"
        />

        {/* Dark gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/25 to-black/75" />

        {/* Hero content — bottom left like the W15 screenshot */}
        <div className="absolute bottom-0 left-0 right-0 px-8 sm:px-16 lg:px-24 pb-28 max-w-3xl">
          <div className="animate-fade-in">
            {/* Location badge */}
            <span className="inline-block mb-4 text-[10px] font-bold tracking-[0.25em] text-skynest-blue border border-skynest-blue/50 px-3 py-1 rounded-full">
              SRI LANKA · COLOMBO · KANDY · GALLE
            </span>

            {/* Hotel name */}
            <h1 className="text-6xl sm:text-7xl lg:text-8xl font-black text-white leading-none tracking-tight mb-4">
              Sky
              <span className="text-skynest-blue">Nest</span>
            </h1>

            {/* Tagline */}
            <p className="text-white/85 text-base sm:text-lg leading-relaxed mb-8 max-w-xl">
              Experience unparalleled luxury at SkyNest Hotels. Three stunning locations
              across Sri Lanka — each offering world-class rooms, exceptional dining,
              and warm island hospitality.
            </p>

            {/* CTA buttons */}
            <div className="flex flex-wrap gap-4">
              <Link
                href="/booking"
                className="inline-flex items-center gap-2 px-8 py-3.5 bg-skynest-blue text-white text-sm font-black tracking-[0.15em] rounded-sm hover:bg-skynest-blue-hover transition-all duration-300 shadow-2xl shadow-skynest-blue/40 group"
              >
                BOOK NOW
                <HiArrowRight
                  size={16}
                  className="group-hover:translate-x-1 transition-transform"
                />
              </Link>
              <a
                href="#about"
                className="inline-flex items-center px-8 py-3.5 border border-white/60 text-white text-sm font-bold tracking-[0.15em] rounded-sm hover:bg-white/10 transition-colors duration-300"
              >
                EXPLORE
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ════════════════════════════════════════════
          STAT STRIP
      ════════════════════════════════════════════ */}
      <section className="bg-skynest-navy">
        <div className="max-w-6xl mx-auto px-8 py-8 grid grid-cols-3 divide-x divide-skynest-navy-light">
          {[
            { number: '3', label: 'LOCATIONS' },
            { number: '50+', label: 'LUXURY ROOMS' },
            { number: '5★', label: 'EXPERIENCE' },
          ].map(stat => (
            <div key={stat.label} className="text-center px-4">
              <div className="text-3xl font-black text-skynest-blue">{stat.number}</div>
              <div className="text-[10px] text-gray-500 tracking-[0.2em] font-semibold mt-1">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ════════════════════════════════════════════
          ABOUT / INTRO SECTION
      ════════════════════════════════════════════ */}
      <section id="about" className="bg-skynest-blue-pale py-20 px-8">
        <div className="max-w-4xl mx-auto text-center">
          <span className="text-[10px] text-skynest-blue font-bold tracking-[0.25em]">
            ABOUT SKYNEST
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-skynest-navy mt-3 mb-5 leading-tight">
            Where Luxury Meets <br className="hidden sm:block" />
            Sri Lankan Warmth
          </h2>
          <p className="text-skynest-muted text-base leading-relaxed max-w-2xl mx-auto mb-8">
            SkyNest Hotels combine contemporary design, relaxed elegance, and individuality
            to create a lasting impression of Sri Lankan hospitality. From our city property in
            Colombo to the scenic hills of Kandy and the colonial charm of Galle — every stay
            is an experience crafted for you.
          </p>
          <Link
            href="/booking"
            className="inline-flex items-center gap-2 px-8 py-3.5 bg-skynest-navy text-white text-sm font-bold tracking-[0.15em] rounded-xl hover:bg-skynest-blue transition-colors duration-300 group"
          >
            START BOOKING
            <HiArrowRight
              size={16}
              className="group-hover:translate-x-1 transition-transform"
            />
          </Link>
        </div>
      </section>

      {/* ════════════════════════════════════════════
          ACCOMMODATIONS TEASER
      ════════════════════════════════════════════ */}
      <section id="accommodations" className="bg-white py-20 px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <span className="text-[10px] text-skynest-blue font-bold tracking-[0.25em]">
              ACCOMMODATIONS
            </span>
            <h2 className="text-3xl font-black text-skynest-navy mt-3">
              Rooms &amp; Suites
            </h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {[
              {
                title: 'Deluxe Room',
                img: 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=600&q=80',
                desc: 'Spacious comfort with city or garden views, king-size bed, and premium amenities.',
              },
              {
                title: 'Executive Suite',
                img: 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=600&q=80',
                desc: 'Elevated luxury with a private lounge, panoramic views, and butler service.',
              },
              {
                title: 'Presidential Suite',
                img: 'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=600&q=80',
                desc: 'The pinnacle of SkyNest hospitality — vast living spaces, private terrace, and bespoke service.',
              },
            ].map(room => (
              <div key={room.title} className="group overflow-hidden rounded-2xl shadow-md hover:shadow-xl transition-shadow">
                <div className="relative h-48 overflow-hidden">
                  <Image
                    src={room.img}
                    alt={room.title}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                </div>
                <div className="p-5 bg-white">
                  <h3 className="font-bold text-skynest-navy">{room.title}</h3>
                  <p className="text-xs text-skynest-muted mt-1 leading-relaxed">{room.desc}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="text-center mt-8">
            <Link
              href="/booking"
              className="inline-flex items-center gap-2 px-8 py-3 bg-skynest-blue text-white text-sm font-bold rounded-xl hover:bg-skynest-blue-hover transition-colors"
            >
              Book a Room <HiArrowRight size={14} />
            </Link>
          </div>
        </div>
      </section>

      {/* ════════════════════════════════════════════
          FOOTER
      ════════════════════════════════════════════ */}
      <footer className="bg-skynest-navy text-gray-400 py-12 px-8">
        <div className="max-w-6xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-8">
          <div>
            <div className="text-xl font-black text-skynest-blue tracking-[0.15em] mb-2">SKYNEST</div>
            <p className="text-xs leading-relaxed">
              Luxury hotel experiences across Colombo, Kandy, and Galle — the finest of Sri Lanka.
            </p>
          </div>
          <div>
            <h4 className="text-white font-bold text-xs tracking-[0.15em] mb-3">LOCATIONS</h4>
            <ul className="space-y-1 text-xs">
              <li>SkyNest Colombo — Colombo 03</li>
              <li>SkyNest Kandy — Central Province</li>
              <li>SkyNest Galle — Galle Fort</li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-bold text-xs tracking-[0.15em] mb-3">CONTACT</h4>
            <ul className="space-y-1 text-xs">
              <li>reservations@skynest.lk</li>
              <li>+94 11 XXX XXXX</li>
              <li>+94 81 XXX XXXX (Kandy)</li>
            </ul>
          </div>
        </div>
        <div className="mt-10 border-t border-skynest-navy-light pt-6 text-center text-[10px] tracking-widest">
          © {new Date().getFullYear()} SKYNEST HOTELS · ALL RIGHTS RESERVED
        </div>
      </footer>
    </>
  );
}
