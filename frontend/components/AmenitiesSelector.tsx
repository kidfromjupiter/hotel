'use client';

import { useState } from 'react';
import { HiCheckCircle } from 'react-icons/hi';
import type { Amenity } from '@/lib/types';

interface AmenitiesSelectorProps {
  amenities: Amenity[];
  roomName: string;
  roomTotal: number;
  nights: number;
  onConfirm: (selected: Amenity[]) => void;
}

const LKR = (n: number) =>
  new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 0,
  }).format(n);

const ICON_MAP: Record<string, string> = {
  car: '🚗',
  spa: '💆',
  coffee: '☕',
  utensils: '🍽️',
  'map-pin': '📍',
  anchor: '⚓',
  breakfast: '🍳',
  airport: '🚗',
};

export default function AmenitiesSelector({
  amenities,
  roomName,
  roomTotal,
  nights,
  onConfirm,
}: AmenitiesSelectorProps) {
  const list = amenities || [];
  const [selected, setSelected] = useState<Set<string>>(new Set());


  const toggle = (id: string) =>
    setSelected(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  const selectedList = list.filter(a => selected.has(a.id));
  const addonsTotal = selectedList.reduce((s, a) => s + a.price, 0);
  const grandTotal = roomTotal + addonsTotal;

  return (
    <div className="max-w-3xl mx-auto animate-slide-up">
      <div className="mb-6">
        <p className="text-skynest-blue text-xs tracking-[0.2em] font-bold mb-1">STEP 3 OF 5</p>
        <h2 className="text-2xl font-bold text-skynest-navy">Enhance Your Stay</h2>
        <p className="text-skynest-muted text-sm mt-1">
          Add optional services to make your stay even more memorable. All prices are one-time additions.
        </p>
      </div>

      {/* ── Amenity grid ── */}
      {list.length === 0 ? (
        <div className="text-center py-10 bg-white rounded-xl border border-gray-200 mb-8 p-6 shadow-sm">
          <p className="text-gray-500 text-sm">No optional add-on amenities currently available for this branch.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          {list.map(amenity => {
            const isOn = selected.has(amenity.id);
            const iconDisplay = ICON_MAP[amenity.icon] || amenity.icon || '✨';
            return (
              <button
                key={amenity.id}
                onClick={() => toggle(amenity.id)}
                className={`text-left p-4 rounded-xl border-2 transition-all duration-200 ${
                  isOn
                    ? 'border-skynest-blue bg-skynest-blue/5 shadow-md shadow-skynest-blue/10'
                    : 'border-gray-200 bg-white hover:border-skynest-blue/40 hover:shadow-sm'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl flex-shrink-0">{iconDisplay}</span>
                    <div>
                      <p className="font-semibold text-skynest-navy text-sm leading-tight">
                        {amenity.name}
                      </p>
                      <p className="text-xs text-skynest-muted mt-0.5 leading-relaxed">
                        {amenity.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                    <span className="text-sm font-bold text-skynest-blue whitespace-nowrap">
                      {LKR(amenity.price)}
                    </span>
                    {isOn && (
                      <HiCheckCircle className="text-skynest-blue" size={18} />
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}

      {/* ── Price breakdown ── */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mb-5">
        <div className="bg-skynest-navy px-6 py-3">
          <h3 className="text-white text-xs font-bold tracking-[0.15em]">PRICE BREAKDOWN</h3>
        </div>
        <div className="px-6 py-5 space-y-2.5 text-sm">
          <div className="flex justify-between text-gray-600">
            <span>
              {roomName}{' '}
              <span className="text-skynest-muted text-xs">
                ({nights} night{nights !== 1 ? 's' : ''})
              </span>
            </span>
            <span className="font-medium text-skynest-navy">{LKR(roomTotal)}</span>
          </div>

          {selectedList.map(a => (
            <div key={a.id} className="flex justify-between text-gray-600">
              <span className="flex items-center gap-1.5">
                <span>{ICON_MAP[a.icon] || a.icon || '✨'}</span> {a.name}
              </span>
              <span className="font-medium text-skynest-navy">{LKR(a.price)}</span>
            </div>
          ))}


          <div className="border-t border-gray-100 pt-3 flex justify-between font-black text-skynest-navy text-base">
            <span>Grand Total</span>
            <span className="text-skynest-blue">{LKR(grandTotal)}</span>
          </div>
        </div>
      </div>

      {/* ── CTA ── */}
      <button
        onClick={() => onConfirm(selectedList)}
        className="w-full py-4 bg-skynest-blue text-white font-bold text-sm tracking-[0.15em] rounded-xl hover:bg-skynest-blue-hover transition-colors shadow-lg shadow-skynest-blue/30"
      >
        CONTINUE TO VERIFICATION
      </button>

      <p className="text-center text-xs text-skynest-muted mt-3">
        You can skip add-ons by clicking Continue without selecting any.
      </p>
    </div>
  );
}
