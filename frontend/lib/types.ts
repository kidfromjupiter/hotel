// ─────────────────────────────────────────────
//  Branch
// ─────────────────────────────────────────────
export interface Branch {
  id: 'colombo' | 'kandy' | 'galle';
  name: string;
  city: string;
  description: string;
  image: string;
  address: string;
}

// ─────────────────────────────────────────────
//  Booking Form
// ─────────────────────────────────────────────
export interface BookingFormData {
  checkIn: string;
  checkOut: string;
  adults: number;
  children: number;
}

// ─────────────────────────────────────────────
//  Room
// ─────────────────────────────────────────────
export interface Room {
  id: string;
  type: string;
  name: string;
  description: string;
  pricePerNight: number;
  totalPrice: number;
  nights: number;
  maxCapacity: number;
  features: string[];
  amenities: Amenity[];
  image: string;
  isBestseller?: boolean;
  /** Price per night for SkyNest members */
  membershipPrice?: number;
  /** Discount percentage for members */
  membershipDiscount?: number;
}

// ─────────────────────────────────────────────
//  Availability API
// ─────────────────────────────────────────────
export interface AvailabilityPayload {
  branch: string;
  checkIn: string;
  checkOut: string;
  adults: number;
  children: number;
}

export interface AvailabilityResponse {
  available: boolean;
  rooms: Room[];
  /**
   * Backend message when no rooms are available, e.g.
   * "No rooms for 8 guests. Max capacity per room is 4."
   */
  message?: string;
  /** Whether the phone number is a registered SkyNest member */
  hasMembership?: boolean;
}

// ─────────────────────────────────────────────
//  Amenities
// ─────────────────────────────────────────────
export interface Amenity {
  id: string;
  name: string;
  description: string;
  price: number;
  icon: string;
}

export interface AmenitiesResponse {
  amenities: Amenity[];
}

// ─────────────────────────────────────────────
//  OTP
// ─────────────────────────────────────────────
export interface SendOTPPayload {
  phone: string;
}

export interface SendOTPResponse {
  success: boolean;
  message: string;
}

export interface VerifyOTPPayload {
  phone: string;
  otp: string;
}

export interface VerifyOTPResponse {
  success: boolean;
  message: string;
}

// ─────────────────────────────────────────────
//  Booking Creation
// ─────────────────────────────────────────────
export interface CreateBookingPayload {
  branch: string;
  checkIn: string;
  checkOut: string;
  adults: number;
  children: number;
  nights: number;
  roomId: string;
  roomType: string;
  totalPrice: number;
  phone: string;
}

export interface CreateBookingResponse {
  success: boolean;
  bookingRef: string;
  message: string;
}

// ─────────────────────────────────────────────
//  Wizard State
// ─────────────────────────────────────────────
export type BookingStep = 'form' | 'rooms' | 'summary' | 'phone' | 'confirmed';

export interface BookingWizardState {
  branch: string;
  checkIn: string;
  checkOut: string;
  adults: number;
  children: number;
  nights: number;
  selectedRoom: Room | null;
  phone: string;
  bookingRef: string;
  hasMembership: boolean;
  totalPrice: number;
}
