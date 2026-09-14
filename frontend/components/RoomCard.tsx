'use client';

import Image from 'next/image';
import { HiCheckCircle, HiStar, HiUserGroup } from 'react-icons/hi';
import type { Room } from '@/lib/types';

interface RoomCardProps {
  room: Room;
  nights: number;
  hasMembership: boolean;
  loading: boolean;
  onSelect: (room: Room) => void;
}

/** Format a number as LKR currency */
const LKR = (amount: number) =>
  new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);

export default function RoomCard({
  room,
  nights,
  hasMembership,
  loading,
  onSelect,
}: RoomCardProps) {
  const pricePerNight =
    hasMembership && room.membershipPrice ? room.membershipPrice : room.pricePerNight;
  const total = pricePerNight * nights;
  const hasMemberDiscount = hasMembership && room.membershipPrice && room.membershipPrice < room.pricePerNight;

  return (
    <div className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden flex flex-col animate-slide-up">

      {/* ── Room image ── */}
      <div className="relative h-52 overflow-hidden">
        <Image
          src={room.image || 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&q=80'}
          alt={room.name}
          fill
          className="object-cover hover:scale-105 transition-transform duration-500"
        />

        {/* Badges */}
        <div className="absolute top-3 left-3 flex gap-2">
          {room.isBestseller && (
            <span className="flex items-center gap-1 bg-skynest-blue text-white text-[10px] font-bold px-2.5 py-1 rounded-full shadow-md">
              <HiStar size={10} /> BESTSELLER
            </span>
          )}
        </div>

        {hasMemberDiscount && (
          <div className="absolute top-3 right-3">
            <span className="bg-amber-400 text-amber-900 text-[10px] font-black px-2.5 py-1 rounded-full shadow-md">
              {room.membershipDiscount ?? ''}% MEMBER OFF
            </span>
          </div>
        )}
      </div>

      {/* ── Content ── */}
      <div className="p-5 flex flex-col flex-1">

        {/* Header row */}
        <div className="flex items-start justify-between gap-3 mb-1">
          <div>
            <span className="text-[10px] text-skynest-blue font-bold tracking-[0.2em] uppercase">
              {room.type}
            </span>
            <h3 className="text-lg font-bold text-skynest-navy mt-0.5 leading-tight">
              {room.name}
            </h3>
          </div>

          {/* Price column */}
          <div className="text-right flex-shrink-0">
            {hasMemberDiscount ? (
              <>
                <p className="text-[11px] text-gray-400 line-through leading-tight">
                  {LKR(room.pricePerNight)}
                </p>
                <p className="text-base font-bold text-skynest-blue leading-tight">
                  {LKR(room.membershipPrice!)}/night
                </p>
              </>
            ) : (
              <p className="text-base font-bold text-skynest-blue leading-tight">
                {LKR(room.pricePerNight)}/night
              </p>
            )}
          </div>
        </div>

        {/* Description */}
        <p className="text-sm text-skynest-muted leading-relaxed mb-3 line-clamp-2">
          {room.description}
        </p>

        {/* Capacity */}
        <div className="flex items-center gap-1 text-xs text-skynest-muted mb-3">
          <HiUserGroup className="text-skynest-blue" />
          <span>Up to {room.maxCapacity} guests</span>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 mb-4">
          {room.features.slice(0, 6).map(f => (
            <div key={f} className="flex items-center gap-1.5 text-xs text-gray-600">
              <HiCheckCircle className="text-skynest-blue flex-shrink-0" size={13} />
              <span className="truncate">{f}</span>
            </div>
          ))}
        </div>

        {/* Membership notice */}
        {hasMembership ? (
          <div className="mb-3 flex items-center gap-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            <span>⭐</span>
            <span>SkyNest Member pricing applied</span>
          </div>
        ) : (
          <div className="mb-3 flex items-center gap-2 text-xs text-skynest-muted bg-skynest-blue-pale rounded-lg px-3 py-2">
            <span>💡</span>
            <span>SkyNest Members enjoy exclusive discounts</span>
          </div>
        )}

        {/* Total + CTA */}
        <div className="mt-auto">
          <div className="flex items-center justify-between px-4 py-3 bg-skynest-blue-pale rounded-xl mb-3">
            <span className="text-sm text-skynest-navy font-medium">
              Total — {nights} night{nights !== 1 ? 's' : ''}
            </span>
            <span className="text-lg font-black text-skynest-navy">{LKR(total)}</span>
          </div>

          <button
            onClick={() => onSelect(room)}
            disabled={loading}
            className="w-full py-3 bg-skynest-navy text-white text-sm font-bold rounded-xl hover:bg-skynest-blue transition-colors duration-300 disabled:opacity-60 disabled:cursor-not-allowed tracking-wide"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Loading...
              </span>
            ) : (
              'Select This Room'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
