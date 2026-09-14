import Image from 'next/image';
import Link from 'next/link';
import { HiLocationMarker, HiArrowRight } from 'react-icons/hi';

interface BranchCardProps {
  id: string;
  name: string;
  city: string;
  description: string;
  image: string;
  address: string;
}

export default function BranchCard({
  id,
  name,
  city,
  description,
  image,
  address,
}: BranchCardProps) {
  return (
    <div className="group relative overflow-hidden rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 bg-white animate-slide-up">

      {/* ── Image ── */}
      <div className="relative h-60 overflow-hidden">
        <Image
          src={image}
          alt={`SkyNest ${city}`}
          fill
          className="object-cover group-hover:scale-110 transition-transform duration-700"
        />
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-skynest-navy/90 via-skynest-navy/20 to-transparent" />

        {/* City badge */}
        <div className="absolute top-4 left-4">
          <span className="bg-skynest-blue text-white text-[10px] font-bold px-3 py-1 rounded-full tracking-[0.15em] shadow-lg">
            {city.toUpperCase()}
          </span>
        </div>

        {/* Name on image */}
        <div className="absolute bottom-4 left-4 right-4">
          <h3 className="text-xl font-bold text-white leading-tight">{name}</h3>
        </div>
      </div>

      {/* ── Content ── */}
      <div className="p-6">
        <div className="flex items-center gap-1.5 text-skynest-muted text-xs mb-3">
          <HiLocationMarker className="text-skynest-blue flex-shrink-0 text-sm" />
          <span>{address}</span>
        </div>

        <p className="text-skynest-muted text-sm leading-relaxed mb-6 line-clamp-3">
          {description}
        </p>

        <Link
          href={`/booking/${id}`}
          className="flex items-center justify-center gap-2 w-full py-3 bg-skynest-navy text-white text-sm font-semibold rounded-xl hover:bg-skynest-blue transition-all duration-300 group/btn"
        >
          <span>Select This Branch</span>
          <HiArrowRight
            size={16}
            className="group-hover/btn:translate-x-1 transition-transform duration-200"
          />
        </Link>
      </div>
    </div>
  );
}
