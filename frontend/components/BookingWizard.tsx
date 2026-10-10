'use client';

import { useState } from 'react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { HiChevronLeft } from 'react-icons/hi';

import type { BookingStep, BookingWizardState, Room, Amenity } from '@/lib/types';
import { checkAvailability } from '@/lib/api';

import StepIndicator from './StepIndicator';
import BookingForm from './BookingForm';
import RoomCard from './RoomCard';

import BookingSummary from './BookingSummary';
import PhoneOTPForm from './PhoneOTPForm';
import BookingConfirmed from './BookingConfirmed';

// ─────────────────────────────────────────────
//  Constants
// ─────────────────────────────────────────────
const STEPS: BookingStep[] = ['form', 'rooms', 'summary', 'phone', 'confirmed'];
const STEP_LABELS = ['Details', 'Select Room', 'Summary', 'Contact', 'Confirmed'];

const BRANCH_DISPLAY: Record<string, string> = {
  colombo: 'Colombo',
  kandy: 'Kandy',
  galle: 'Galle',
};

// ─────────────────────────────────────────────
//  Room Type Visual Metadata & Descriptions
// ─────────────────────────────────────────────
const ROOM_TYPE_CONFIG: Record<string, {
  name: string;
  type: string;
  description: string;
  features: string[];
  image: string;
  isBestseller?: boolean;
  maxCapacity: number;
  membershipDiscount: number;
}> = {
  STANDARD: {
    name: 'Standard Room',
    type: 'Standard Room',
    description: 'Comfortable and elegant room equipped with modern amenities, plush bedding, and scenic views.',
    features: ['Queen Bed', 'Air Conditioning', 'Free High-Speed Wi-Fi', 'En-suite Bathroom', 'Smart TV', 'Tea & Coffee Maker'],
    image: 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80',
    isBestseller: false,
    maxCapacity: 2,
    membershipDiscount: 10,
  },
  DELUXE: {
    name: 'Deluxe Room',
    type: 'Deluxe Room',
    description: 'Spacious sanctuary featuring a private balcony, luxury king bed, premium bath amenities, and panoramic ocean or skyline views.',
    features: ['King Bed', 'Private Balcony', 'Bathtub & Rain Shower', 'Minibar', 'Ocean / Scenic View', '24/7 Room Service'],
    image: 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&q=80',
    isBestseller: true,
    maxCapacity: 2,
    membershipDiscount: 15,
  },
  SUITE: {
    name: 'Executive Suite',
    type: 'Executive Suite',
    description: 'Elevated luxury with a private lounge, panoramic ocean views, luxury king bed, jacuzzi bath, and dedicated butler service.',
    features: ['King Bed', 'Private Lounge', 'Luxury Jacuzzi & Bath', 'Panoramic View', 'Complimentary Minibar', '24/7 Butler Service'],
    image: 'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80',
    isBestseller: false,
    maxCapacity: 2,
    membershipDiscount: 20,
  },
  FAMILY: {
    name: 'Family Suite',
    type: 'Family Suite',
    description: 'Spacious accommodation designed for families with interconnecting sleeping zones, kid amenities, and large living area.',
    features: ['1 King + 2 Twin Beds', 'Living Area', '2 En-suite Bathrooms', 'Kid-friendly Amenities', 'Smart TV & Console'],
    image: 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800&q=80',
    isBestseller: false,
    maxCapacity: 4,
    membershipDiscount: 15,
  },
};

/**
 * Groups raw database rooms by Room Type to eliminate duplicate cards
 * and calculates the available inventory count for each category.
 */
function groupAvailableRooms(
  rawRooms: Room[],
  nights: number,
  hasMembership: boolean
): Room[] {
  const groups = new Map<string, Room[]>();

  for (const r of rawRooms) {
    const rawType = (r as any).room_type_id || r.type || 'STANDARD';
    const cleanType = String(rawType).toUpperCase().replace(/[^A-Z]/g, '');
    let typeKey = 'STANDARD';
    if (cleanType.includes('DELUXE')) typeKey = 'DELUXE';
    else if (cleanType.includes('SUITE') && cleanType.includes('FAMILY')) typeKey = 'FAMILY';
    else if (cleanType.includes('FAMILY')) typeKey = 'FAMILY';
    else if (cleanType.includes('SUITE')) typeKey = 'SUITE';
    else if (cleanType.includes('STANDARD')) typeKey = 'STANDARD';
    else typeKey = cleanType || 'STANDARD';

    if (!groups.has(typeKey)) {
      groups.set(typeKey, []);
    }
    groups.get(typeKey)!.push(r);
  }

  const result: Room[] = [];

  for (const [typeKey, roomsInGroup] of groups.entries()) {
    const firstRoom = roomsInGroup[0];
    const config = ROOM_TYPE_CONFIG[typeKey] || {
      name: `${typeKey.charAt(0) + typeKey.slice(1).toLowerCase()} Room`,
      type: `${typeKey.charAt(0) + typeKey.slice(1).toLowerCase()} Room`,
      description: firstRoom.description || 'Comfortable and elegant room equipped with modern amenities and scenic views.',
      features: firstRoom.features?.length ? firstRoom.features : ['Air Conditioning', 'Free Wi-Fi', 'En-suite Bathroom', 'Smart TV'],
      image: firstRoom.image || 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80',
      isBestseller: false,
      maxCapacity: firstRoom.maxCapacity || 2,
      membershipDiscount: 10,
    };

    const pricePerNight = firstRoom.pricePerNight || 15000;
    const membershipDiscount = config.membershipDiscount;
    const membershipPrice = firstRoom.membershipPrice || Math.round(pricePerNight * (1 - membershipDiscount / 100));
    const effectiveRate = hasMembership && membershipPrice ? membershipPrice : pricePerNight;
    const totalPrice = effectiveRate * nights;

    result.push({
      id: firstRoom.id,
      roomNumber: firstRoom.roomNumber,
      type: config.type,
      name: config.name,
      description: config.description,
      pricePerNight,
      totalPrice,
      nights,
      maxCapacity: config.maxCapacity || firstRoom.maxCapacity || 2,
      features: config.features,
      amenities: firstRoom.amenities || [],
      image: config.image,
      isBestseller: config.isBestseller,
      membershipPrice,
      membershipDiscount,
      roomsLeft: roomsInGroup.length,
      availableRooms: roomsInGroup,
    });
  }

  return result;
}

// ─────────────────────────────────────────────
//  BookingWizard — multi-step booking flow
// ─────────────────────────────────────────────
interface Props {
  branch: string;
}

export default function BookingWizard({ branch }: Props) {
  const branchName = BRANCH_DISPLAY[branch] ?? branch;

  // ── Step management ──────────────────────────
  const [step, setStep] = useState<BookingStep>('form');
  const currentIndex = STEPS.indexOf(step);

  // ── Loading & error states ───────────────────
  const [loadingAvail, setLoadingAvail] = useState(false);
  const [availError, setAvailError] = useState<string | null>(null);
  const [noRoomMsg, setNoRoomMsg] = useState<string | null>(null);

  // ── Data ─────────────────────────────────────
  const [availableRooms, setAvailableRooms] = useState<Room[]>([]);

  const [state, setState] = useState<BookingWizardState>({
    branch,
    checkIn: '',
    checkOut: '',
    adults: 1,
    children: 0,
    nights: 1,
    selectedRoom: null,
    phone: '',
    bookingRef: '',
    hasMembership: false,
    totalPrice: 0,
  });

  // ── Helpers ───────────────────────────────────
  const calcNights = (ci: string, co: string) =>
    Math.max(1, Math.ceil((new Date(co).getTime() - new Date(ci).getTime()) / 86_400_000));

  const goBack = () => {
    if (step === 'summary') {
      setStep('rooms');
    } else if (step === 'phone') {
      setStep('summary');
    } else {
      setStep(STEPS[Math.max(0, currentIndex - 1)]);
    }
  };

  // ─────────────────────────────────────────────
  //  STEP 1 → 2 : Check Availability
  // ─────────────────────────────────────────────
  const handleFormSubmit = async (formData: {
    checkIn: string;
    checkOut: string;
    adults: number;
    children: number;
  }) => {
    setLoadingAvail(true);
    setAvailError(null);
    setNoRoomMsg(null);

    try {
      const nights = calcNights(formData.checkIn, formData.checkOut);
      const res = await checkAvailability({ branch, ...formData });

      setState(prev => ({
        ...prev,
        ...formData,
        nights,
        hasMembership: res.hasMembership ?? false,
      }));

      if (!res.available || !res.rooms?.length) {
        setAvailableRooms([]);
        setNoRoomMsg(
          res.message ??
          'No rooms are available for the selected dates and guest count. Please try different dates or fewer guests.'
        );
      } else {
        // Group individual physical rooms by Room Type to eliminate duplicate room cards
        const groupedRooms = groupAvailableRooms(
          res.rooms as Room[],
          nights,
          res.hasMembership ?? false
        );
        setAvailableRooms(groupedRooms);
        setNoRoomMsg(null);
      }

      setStep('rooms');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to check availability.';
      setAvailError(msg);
      toast.error(msg);
    } finally {
      setLoadingAvail(false);
    }
  };

  // ─────────────────────────────────────────────
  //  STEP 2 → 3 : Room Selected
  // ─────────────────────────────────────────────
  const handleRoomSelect = (room: Room) => {
    setState(prev => ({
      ...prev,
      selectedRoom: room,
      totalPrice: room.totalPrice,
    }));
    setStep('summary');
  };

  // ─────────────────────────────────────────────
  //  STEP 4 → 5 : Summary Reviewed → Phone Input
  // ─────────────────────────────────────────────
  const handleSummaryContinue = () => {
    setStep('phone');
  };

  // ─────────────────────────────────────────────
  //  STEP 5 → 6 : Phone Submitted → Booking Confirmed
  // ─────────────────────────────────────────────
  const handlePhoneComplete = (
    phone: string,
    bookingRef: string,
    details?: {
      firstName?: string;
      lastName?: string;
      email?: string;
      specialRequests?: string;
      nationalId?: string;
    }
  ) => {
    setState(prev => ({
      ...prev,
      phone,
      bookingRef,
      firstName: details?.firstName,
      lastName: details?.lastName,
      email: details?.email,
      specialRequests: details?.specialRequests,
      nationalId: details?.nationalId,
    }));
    setStep('confirmed');
  };

  // ─────────────────────────────────────────────
  //  Render
  // ─────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-skynest-blue-pale pt-16 print:min-h-0 print:pt-0 print:bg-white">

      {/* ── Page header ── */}
      <div className="bg-skynest-navy text-white py-6 px-4 shadow-lg print:hidden">
        <div className="max-w-6xl mx-auto">
          {/* Back navigation */}
          {step !== 'confirmed' && (
            <div className="mb-3">
              {step === 'form' ? (
                <Link
                  href="/booking"
                  className="inline-flex items-center gap-0.5 text-skynest-blue-light text-xs hover:text-white transition-colors font-medium tracking-wide"
                >
                  <HiChevronLeft size={16} /> All Branches
                </Link>
              ) : (
                <button
                  onClick={goBack}
                  className="inline-flex items-center gap-0.5 text-skynest-blue-light text-xs hover:text-white transition-colors font-medium tracking-wide"
                >
                  <HiChevronLeft size={16} /> Back
                </button>
              )}
            </div>
          )}

          {/* Title */}
          <h1 className="text-xl font-bold">
            <span className="text-white">SkyNest </span>
            <span className="text-skynest-blue">{branchName}</span>
            <span className="text-gray-500 font-normal text-sm ml-2">— Reservation</span>
          </h1>

          <StepIndicator steps={STEP_LABELS} currentStep={currentIndex} />
        </div>
      </div>

      {/* ── Main content ── */}
      <div className="max-w-6xl mx-auto px-4 py-10 print:max-w-none print:p-0 print:m-0">

        {/* Non-blocking availability error */}
        {availError && step === 'form' && (
          <div className="mb-6 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            {availError}
          </div>
        )}

        {/* ── STEP 1: Booking Form (Details) ── */}
        {step === 'form' && (
          <BookingForm
            branchName={branchName}
            onSubmit={handleFormSubmit}
            loading={loadingAvail}
          />
        )}

        {/* ── STEP 2: Room Selection (Standard & Deluxe) ── */}
        {step === 'rooms' && (
          <div className="animate-slide-up">
            {/* Membership banner */}
            {state.hasMembership && (
              <div className="mb-5 flex items-center gap-3 px-5 py-3 bg-amber-50 border border-amber-300 rounded-2xl shadow-sm">
                <span className="text-2xl">⭐</span>
                <div>
                  <p className="font-bold text-amber-800 text-sm">SkyNest Member Detected!</p>
                  <p className="text-amber-600 text-xs">
                    Member pricing has been automatically applied to all available rooms.
                  </p>
                </div>
              </div>
            )}

            <div className="flex flex-wrap items-baseline justify-between gap-2 mb-5">
              <div>
                <p className="text-skynest-blue text-xs tracking-[0.2em] font-bold mb-0.5 uppercase">STEP 2 OF 5</p>
                <h2 className="text-2xl font-bold text-skynest-navy">Available Rooms</h2>
                <p className="text-xs text-skynest-muted mt-0.5">
                  Select your preferred room type from the available options below.
                </p>
              </div>
              <p className="text-sm text-skynest-muted bg-white px-3 py-1.5 rounded-full border border-gray-200 shadow-sm">
                🌙 {state.nights} night{state.nights !== 1 ? 's' : ''} &nbsp;·&nbsp;
                👤 {state.adults} adult{state.adults !== 1 ? 's' : ''}
                {state.children > 0 && ` · 🧒 ${state.children} child${state.children !== 1 ? 'ren' : ''}`}
              </p>
            </div>

            {/* No rooms state */}
            {noRoomMsg ? (
              <div className="text-center bg-white border border-amber-200 rounded-2xl p-10 shadow-sm">
                <div className="text-6xl mb-4">🏨</div>
                <h3 className="text-xl font-bold text-amber-800 mb-2">No Rooms Available</h3>
                <p className="text-amber-700 text-sm max-w-md mx-auto leading-relaxed mb-6">
                  {noRoomMsg}
                </p>
                <button
                  onClick={() => setStep('form')}
                  className="px-6 py-2.5 bg-skynest-blue text-white text-sm font-bold rounded-xl hover:bg-skynest-blue-hover transition-colors"
                >
                  Change Dates / Guests
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {availableRooms.map(room => (
                  <RoomCard
                    key={room.type || room.id}
                    room={room}
                    nights={state.nights}
                    hasMembership={state.hasMembership}
                    onSelect={handleRoomSelect}
                  />
                ))}
              </div>
            )}
          </div>
        )}



        {/* ── STEP 4: Booking Summary & Review ── */}
        {step === 'summary' && (
          <BookingSummary
            booking={state}
            onBack={() => setStep('rooms')}
            onContinue={handleSummaryContinue}
          />
        )}

        {/* ── STEP 5: Phone Number Input & Submit to Backend ── */}
        {step === 'phone' && state.selectedRoom && (
          <PhoneOTPForm
            bookingData={{
              branch: state.branch,
              checkIn: state.checkIn,
              checkOut: state.checkOut,
              adults: state.adults,
              children: state.children,
              nights: state.nights,
              roomId: state.selectedRoom.id,
              roomType: state.selectedRoom.name,
              totalPrice: state.totalPrice,
            }}
            onBack={() => setStep('summary')}
            onComplete={handlePhoneComplete}
          />
        )}

        {/* ── STEP 6: Final Confirmation & Receptionist OTP ── */}
        {step === 'confirmed' && (
          <BookingConfirmed booking={state} />
        )}
      </div>
    </div>
  );
}
