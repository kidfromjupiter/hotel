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
//  Rooms / Availability
// ─────────────────────────────────────────────

/**
 * POST /api/rooms/availability
 * Checks room availability for the given branch, dates, and guest count.
 * Backend returns available rooms (with prices), member status, and
 * an optional message when no rooms are suitable.
 */
export async function checkAvailability(
  data: AvailabilityPayload
): Promise<AvailabilityResponse> {
  return request<AvailabilityResponse>('/api/rooms/availability', {
    method: 'POST',
    body: JSON.stringify(data),
  });
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
  return request<CreateBookingResponse>('/api/booking/create', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
