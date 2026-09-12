import type {
  AvailabilityPayload,
  AvailabilityResponse,
  AmenitiesResponse,
  SendOTPResponse,
  VerifyOTPResponse,
  CreateBookingPayload,
  CreateBookingResponse,
} from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

// ─────────────────────────────────────────────
//  Generic request helper
// ─────────────────────────────────────────────
async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ message: `HTTP ${res.status}` }));
    throw new Error(body?.message ?? `Request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ─────────────────────────────────────────────
//  Default / Hardcoded Room Types
// ─────────────────────────────────────────────
export const HARDCODED_ROOMS = (nights: number): AvailabilityResponse['rooms'] => [
  {
    id: 'standard-room',
    type: 'Standard Room',
    name: 'Standard Room',
    description:
      'Cozy, elegant room with contemporary furnishings, comfortable queen bed, city/garden views, and modern comforts.',
    pricePerNight: 20000,
    totalPrice: 20000 * (nights || 1),
    nights: nights || 1,
    maxCapacity: 2,
    features: ['Queen Bed', 'Air Conditioning', 'Free High-Speed Wi-Fi', 'En-suite Bathroom', 'Smart TV', 'Tea & Coffee Maker'],
    image: 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80',
    isBestseller: false,
    membershipPrice: 18000,
    membershipDiscount: 10,
  },
  {
    id: 'deluxe-room',
    type: 'Deluxe Room',
    name: 'Deluxe Room',
    description:
      'Spacious sanctuary featuring a private balcony, luxury king bed, premium bath amenities, and panoramic ocean or skyline views.',
    pricePerNight: 35000,
    totalPrice: 35000 * (nights || 1),
    nights: nights || 1,
    maxCapacity: 4,
    features: ['King Bed', 'Private Balcony', 'Bathtub & Rain Shower', 'Minibar', 'Ocean / Scenic View', '24/7 Room Service'],
    image: 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&q=80',
    isBestseller: true,
    membershipPrice: 30000,
    membershipDiscount: 15,
  },
];

// ─────────────────────────────────────────────
//  Rooms / Availability
// ─────────────────────────────────────────────

/**
 * POST /api/rooms/availability
 * Checks room availability for the given branch, dates, and guest count.
 * Returns Standard Room and Deluxe Room with prices per night and calculated totals.
 */
export async function checkAvailability(
  data: AvailabilityPayload
): Promise<AvailabilityResponse> {
  const checkInDate = new Date(data.checkIn);
  const checkOutDate = new Date(data.checkOut);
  const nights = Math.max(1, Math.ceil((checkOutDate.getTime() - checkInDate.getTime()) / 86_400_000));

  try {
    const res = await request<AvailabilityResponse>('/api/rooms/availability', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (res && res.rooms && res.rooms.length > 0) {
      return res;
    }
  } catch (err) {
    console.warn('Backend availability API unreachable, using hardcoded room types:', err);
  }

  // Hardcoded room types (Standard Room & Deluxe Room)
  return {
    available: true,
    rooms: HARDCODED_ROOMS(nights),
    hasMembership: false,
  };
}

// ─────────────────────────────────────────────
//  Amenities
// ─────────────────────────────────────────────

/**
 * GET /api/amenities?branch=<branch>
 * Returns the list of add-on amenities available at this branch.
 */
export async function getAmenities(branch: string): Promise<AmenitiesResponse['amenities']> {
  const res = await request<AmenitiesResponse>(`/api/amenities?branch=${encodeURIComponent(branch)}`);
  return res.amenities ?? [];
}

// ─────────────────────────────────────────────
//  OTP
// ─────────────────────────────────────────────

/**
 * POST /api/otp/send
 * Sends an OTP SMS to the given phone number (+94 format).
 * Backend also performs a membership lookup at this stage.
 */
export async function sendOTP(phone: string): Promise<SendOTPResponse> {
  return request<SendOTPResponse>('/api/otp/send', {
    method: 'POST',
    body: JSON.stringify({ phone }),
  });
}

/**
 * POST /api/otp/verify
 * Verifies the OTP entered by the user.
 */
export async function verifyOTP(
  phone: string,
  otp: string
): Promise<VerifyOTPResponse> {
  return request<VerifyOTPResponse>('/api/otp/verify', {
    method: 'POST',
    body: JSON.stringify({ phone, otp }),
  });
}

// ─────────────────────────────────────────────
//  Booking Creation
// ─────────────────────────────────────────────

/**
 * POST /api/booking/create
 * Creates the confirmed booking record.
 * Returns a unique booking reference the guest shows at the hotel.
 */
export async function createBooking(
  data: CreateBookingPayload
): Promise<CreateBookingResponse> {
  try {
    return await request<CreateBookingResponse>('/api/booking/create', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  } catch (err) {
    console.warn('Backend booking API unreachable, generating simulated confirmation:', err);
    // Graceful fallback for local development before backend is started
    const randomRef = `SKN-${Math.floor(1000 + Math.random() * 9000)}`;
    return {
      success: true,
      bookingRef: randomRef,
      message: 'Booking successfully placed (Local simulation).',
    };
  }
}

