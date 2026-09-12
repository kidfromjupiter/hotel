'use client';

import { useState } from 'react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { HiChevronLeft } from 'react-icons/hi';

import type { BookingStep, BookingWizardState, Room, Amenity } from '@/lib/types';
import { checkAvailability, getAmenities } from '@/lib/api';

import StepIndicator from './StepIndicator';
import BookingForm from './BookingForm';
import RoomCard from './RoomCard';
import AmenitiesSelector from './AmenitiesSelector';
import BookingSummary from './BookingSummary';
import PhoneOTPForm from './PhoneOTPForm';
import BookingConfirmed from './BookingConfirmed';

// ─────────────────────────────────────────────
//  Constants
// ─────────────────────────────────────────────
const STEPS: BookingStep[] = ['form', 'rooms', 'amenities', 'summary', 'phone', 'confirmed'];
const STEP_LABELS = ['Details', 'Select Room', 'Add-ons', 'Summary', 'Contact', 'Confirmed'];

const BRANCH_DISPLAY: Record<string, string> = {
  colombo: 'Colombo',
  kandy: 'Kandy',
  galle: 'Galle',
};

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
  const [loadingAmenities, setLoadingAmenities] = useState(false);
  const [availError, setAvailError] = useState<string | null>(null);
  const [noRoomMsg, setNoRoomMsg] = useState<string | null>(null);

  // ── Data ─────────────────────────────────────
  const [availableRooms, setAvailableRooms] = useState<Room[]>([]);
  const [amenitiesList, setAmenitiesList] = useState<Amenity[]>([]);

  const [state, setState] = useState<BookingWizardState>({
    branch,
    checkIn: '',
    checkOut: '',
    adults: 1,
    children: 0,
    nights: 1,
    selectedRoom: null,
    selectedAmenities: [],
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
      setStep('amenities');
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
        // Ensure totalPrice reflects the calculated nights
        const roomsWithNights = res.rooms.map(r => ({
          ...r,
          nights,
          totalPrice: (r.membershipPrice && res.hasMembership ? r.membershipPrice : r.pricePerNight) * nights,
        }));
        setAvailableRooms(roomsWithNights);
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
  const handleRoomSelect = async (room: Room) => {
    setState(prev => ({
      ...prev,
      selectedRoom: room,
      totalPrice: room.totalPrice,
    }));
    setLoadingAmenities(true);

    try {
      const list = await getAmenities(branch);
      setAmenitiesList(list);
    } catch {
      setAmenitiesList([]); // AmenitiesSelector has built-in fallback
    } finally {
      setLoadingAmenities(false);
      setStep('amenities');
    }
  };

  // ─────────────────────────────────────────────
  //  STEP 3 → 4 : Amenities Confirmed → Review Summary
  // ─────────────────────────────────────────────
  const handleAmenitiesConfirm = (selected: Amenity[]) => {
    const addonsTotal = selected.reduce((s, a) => s + a.price, 0);
    const roomPricePerNight = state.hasMembership && state.selectedRoom?.membershipPrice
      ? state.selectedRoom.membershipPrice
      : (state.selectedRoom?.pricePerNight ?? 0);
    const roomTotal = roomPricePerNight * (state.nights || 1);

    setState(prev => ({
      ...prev,
      selectedAmenities: selected,
      totalPrice: roomTotal + addonsTotal,
    }));
    // Goes to clear, complete booking summary step
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
  const handlePhoneComplete = (phone: string, bookingRef: string) => {
    setState(prev => ({ ...prev, phone, bookingRef }));
    setStep('confirmed');
  };

  // ─────────────────────────────────────────────
  //  Render
  // ─────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-skynest-blue-pale pt-16">

      {/* ── Page header ── */}
      <div className="bg-skynest-navy text-white py-6 px-4 shadow-lg">
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
      <div className="max-w-6xl mx-auto px-4 py-10">

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
                <p className="text-skynest-blue text-xs tracking-[0.2em] font-bold mb-0.5 uppercase">STEP 2 OF 6</p>
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
                    key={room.id}
                    room={room}
                    nights={state.nights}
                    hasMembership={state.hasMembership}
                    loading={loadingAmenities}
                    onSelect={handleRoomSelect}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── STEP 3: Extra Amenities Selection ── */}
        {step === 'amenities' && state.selectedRoom && (
          <AmenitiesSelector
            amenities={amenitiesList}
            roomName={state.selectedRoom.name}
            roomTotal={state.selectedRoom.totalPrice}
            nights={state.nights}
            onConfirm={handleAmenitiesConfirm}
          />
        )}

        {/* ── STEP 4: Booking Summary & Review ── */}
        {step === 'summary' && (
          <BookingSummary
            booking={state}
            onBack={() => setStep('amenities')}
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
              amenityIds: state.selectedAmenities.map(a => a.id),
              amenities: state.selectedAmenities,
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
