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
  /** Room number from the database (used as key in lists) */
  roomNumber?: number;
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

/** Room as returned by GET /api/v1/rooms/all — used in Receptionist & Admin room grids */
export interface HotelRoom {
  room_number: number;
  branch_id: number;
  room_type_id: string;
  room_status: 'AVAILABLE' | 'OCCUPIED' | 'MAINTENANCE';
  type_name?: string;
  capacity: number | null;
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

// ─────────────────────────────────────────────
//  MANAGEMENT UI (RECEPTIONIST) TYPES
//  Based on Database ER Diagram
// ─────────────────────────────────────────────

export interface GuestProfile {
  guestId: number;
  name: string;
  phone: string;
  nationalId?: string;
  membershipId?: number;
}

export type BookingStatus = 'Confirmed' | 'Checked-In' | 'Checked-Out' | 'Cancelled';

export interface StaffBooking {
  bookingId: number;
  guestName: string;
  phone: string;
  branchId: number;
  bookingReference: string;
  roomNumber: number;
  roomType: string;
  checkIn: string; // YYYY-MM-DD
  checkOut: string; // YYYY-MM-DD
  status: BookingStatus;
  adults: number;
  children: number;
}

export interface ServiceCatalogueItem {
  serviceId: number;
  serviceName: string;
  dayRate: number;
}

export interface InvoiceSummary {
  invoiceId: string; // UUID
  bookingId: number;
  totalRoomCharges: number;
  totalAmenityCharges: number;
  totalServiceCharges: number;
  totalTaxAmount: number;
  grandTotal: number;
  amountPaid: number;
  paymentStatus: 'Paid' | 'Partial' | 'Unpaid';
}

// ─────────────────────────────────────────────
//  MANAGEMENT UI (ADMIN) TYPES
// ─────────────────────────────────────────────

export interface AdminBranch {
  id: number;
  name: string;
  location: string;
  phone: string;
  email: string;
  rooms: number;
  status: string;
}

export interface BranchItem {
  branch_id: number;
  branch_name: string;
}

export interface AdminRoom {
  id: number;
  type: string;
  branch: string;
  price: string;
  status: string;
}

export interface FormattedService {
  id: number;
  name: string;
  category: string;
  price: string;
  status: string;
}

export interface ExpectedGuest {
  id: string;
  guest: string;
  checkInDate: string;
  status: string;
  phone: string;
  isMember: boolean;
}
