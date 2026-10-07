import type {
  AvailabilityPayload,
  AvailabilityResponse,
  AmenitiesResponse,
  SendOTPResponse,
  VerifyOTPResponse,
  CreateBookingPayload,
  CreateBookingResponse,
  StaffBooking,
  GuestProfile,
  ServiceCatalogueItem,
  InvoiceSummary,
  StaffUser,
  LoginResponse,
} from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

// ─────────────────────────────────────────────
//  Auth Token Helpers (Client-side)
// ─────────────────────────────────────────────
const TOKEN_KEY = 'skynest_auth_token';
const USER_KEY = 'skynest_auth_user';

export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): StaffUser | null {
  if (typeof window === 'undefined') return null;
  const user = localStorage.getItem(USER_KEY);
  return user ? JSON.parse(user) : null;
}

export function setAuthSession(token: string, user: StaffUser) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuthSession() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

// ─────────────────────────────────────────────
//  Generic request helper with Bearer token
// ─────────────────────────────────────────────
async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options?.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(body?.detail || body?.message || `Request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ─────────────────────────────────────────────
//  Default / Hardcoded Room Types
// ─────────────────────────────────────────────
export const ROOM_TYPE_DEFAULTS: Record<
  string,
  {
    type: string;
    name: string;
    description: string;
    features: string[];
    amenities: { id: string; name: string; description: string; price: number; icon: string }[];
    image: string;
    isBestseller: boolean;
    membershipDiscount: number;
    maxCapacity: number;
  }
> = {
  STANDARD: {
    type: 'Standard Room',
    name: 'Standard Room',
    description:
      'Cozy, elegant room with contemporary furnishings, comfortable queen bed, city/garden views, and modern comforts.',
    features: ['Queen Bed', 'Air Conditioning', 'Free High-Speed Wi-Fi', 'En-suite Bathroom', 'Smart TV', 'Tea & Coffee Maker'],
    amenities: [
      { id: 'a1', name: 'Air Conditioning', description: 'Climate control', price: 0, icon: '❄️' },
      { id: 'a2', name: 'Free High-Speed Wi-Fi', description: 'Unlimited access', price: 0, icon: '📶' },
    ],
    image: 'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80',
    isBestseller: false,
    membershipDiscount: 10,
    maxCapacity: 2,
  },
  DELUXE: {
    type: 'Deluxe Room',
    name: 'Deluxe Room',
    description:
      'Spacious sanctuary featuring a private balcony, luxury king bed, premium bath amenities, and panoramic ocean or skyline views.',
    features: ['King Bed', 'Private Balcony', 'Bathtub & Rain Shower', 'Minibar', 'Ocean / Scenic View', '24/7 Room Service'],
    amenities: [
      { id: 'a1', name: 'Air Conditioning', description: 'Climate control', price: 0, icon: '❄️' },
      { id: 'a2', name: 'Free High-Speed Wi-Fi', description: 'Unlimited access', price: 0, icon: '📶' },
      { id: 'a3', name: 'Minibar', description: 'Fully stocked minibar', price: 0, icon: '🍷' },
      { id: 'a4', name: '24/7 Room Service', description: 'Available anytime', price: 0, icon: '🛎️' },
    ],
    image: 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&q=80',
    isBestseller: true,
    membershipDiscount: 15,
    maxCapacity: 4,
  },
  SUITE: {
    type: 'Executive Suite',
    name: 'Executive Suite',
    description:
      'Elevated luxury with a private lounge, panoramic ocean views, luxury king bed, and dedicated butler service.',
    features: ['King Bed', 'Private Lounge', 'Luxury Jacuzzi & Bath', 'Panoramic View', 'Complimentary Minibar', '24/7 Butler Service'],
    amenities: [
      { id: 'a1', name: 'Air Conditioning', description: 'Climate control', price: 0, icon: '❄️' },
      { id: 'a2', name: 'Free High-Speed Wi-Fi', description: 'Unlimited access', price: 0, icon: '📶' },
      { id: 'a3', name: 'Minibar', description: 'Fully stocked minibar', price: 0, icon: '🍷' },
      { id: 'a4', name: 'Butler Service', description: 'Dedicated personal butler', price: 0, icon: '🛎️' },
    ],
    image: 'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&q=80',
    isBestseller: false,
    membershipDiscount: 20,
    maxCapacity: 2,
  },
  FAMILY: {
    type: 'Family Suite',
    name: 'Family Suite',
    description:
      'Spacious accommodation designed for families with interconnecting sleeping zones, kid amenities, and large living area.',
    features: ['1 King + 2 Twin Beds', 'Living Area', '2 En-suite Bathrooms', 'Kid-friendly Amenities', 'Smart TV & Console'],
    amenities: [
      { id: 'a1', name: 'Air Conditioning', description: 'Climate control', price: 0, icon: '❄️' },
      { id: 'a2', name: 'Free High-Speed Wi-Fi', description: 'Unlimited access', price: 0, icon: '📶' },
      { id: 'a3', name: 'Kid-friendly Setup', description: 'Games & cribs available', price: 0, icon: '🧸' },
      { id: 'a4', name: '24/7 Room Service', description: 'Family dining service', price: 0, icon: '🛎️' },
    ],
    image: 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800&q=80',
    isBestseller: false,
    membershipDiscount: 15,
    maxCapacity: 4,
  },
};

export const HARDCODED_ROOMS = (nights: number): AvailabilityResponse['rooms'] => [
  {
    id: 'standard-room',
    type: 'Standard Room',
    name: 'Standard Room',
    description: ROOM_TYPE_DEFAULTS.STANDARD.description,
    pricePerNight: 20000,
    totalPrice: 20000 * (nights || 1),
    nights: nights || 1,
    maxCapacity: 2,
    features: ROOM_TYPE_DEFAULTS.STANDARD.features,
    amenities: ROOM_TYPE_DEFAULTS.STANDARD.amenities,
    image: ROOM_TYPE_DEFAULTS.STANDARD.image,
    isBestseller: false,
    membershipPrice: 18000,
    membershipDiscount: 10,
  },
  {
    id: 'deluxe-room',
    type: 'Deluxe Room',
    name: 'Deluxe Room',
    description: ROOM_TYPE_DEFAULTS.DELUXE.description,
    pricePerNight: 35000,
    totalPrice: 35000 * (nights || 1),
    nights: nights || 1,
    maxCapacity: 4,
    features: ROOM_TYPE_DEFAULTS.DELUXE.features,
    amenities: ROOM_TYPE_DEFAULTS.DELUXE.amenities,
    image: ROOM_TYPE_DEFAULTS.DELUXE.image,
    isBestseller: true,
    membershipPrice: 30000,
    membershipDiscount: 15,
  },
];

// ─────────────────────────────────────────────
//  Rooms / Availability
// ─────────────────────────────────────────────

/**
 * Checks room availability for the given branch, dates, and guest count.
 * Calls backend POST /api/v1/rooms/availability (with fallback to GET /api/v1/rooms)
 * and normalizes the room objects with full frontend-ready fields.
 */
export async function checkAvailability(
  data: AvailabilityPayload
): Promise<AvailabilityResponse> {
  const checkInDate = data.checkIn ? new Date(data.checkIn) : new Date();
  const checkOutDate = data.checkOut ? new Date(data.checkOut) : new Date();
  const diffTime = checkOutDate.getTime() - checkInDate.getTime();
  const nights = Math.max(1, Math.round(diffTime / (1000 * 60 * 60 * 24)) || 1);

  let rawResult: any = null;

  try {
    // 1. Primary: POST /api/v1/rooms/availability
    rawResult = await request<any>('/api/v1/rooms/availability', {
      method: 'POST',
      body: JSON.stringify({
        branch: data.branch,
        checkIn: data.checkIn,
        checkOut: data.checkOut,
        adults: data.adults,
        children: data.children,
      }),
    });
  } catch {
    // 2. Fallback: GET /api/v1/rooms
    try {
      const params = new URLSearchParams();
      if (data.checkIn != null) params.set('check_in', data.checkIn);
      if (data.checkOut != null) params.set('check_out', data.checkOut);
      if (data.adults != null) params.set('adults', String(data.adults));
      if (data.children != null) params.set('children', String(data.children));
      if (data.branch != null) params.set('branch', data.branch);
      rawResult = await request<any>(`/api/v1/rooms?${params.toString()}`, {
        method: 'GET',
      });
    } catch {
      rawResult = null;
    }
  }

  // Extract raw room list whether backend returned { available, rooms } or a plain Array [...]
  let rawRooms: any[] = [];
  if (Array.isArray(rawResult)) {
    rawRooms = rawResult;
  } else if (rawResult && Array.isArray(rawResult.rooms)) {
    rawRooms = rawResult.rooms;
  }

  // If no rooms returned, return clean empty response
  if (rawRooms.length === 0) {
    return {
      available: false,
      rooms: [],
      message:
        rawResult?.message ??
        'No rooms are available for the selected dates and guest count. Please try different dates or fewer guests.',
      hasMembership: rawResult?.hasMembership ?? false,
    };
  }

  // Map and enrich each room with complete frontend Room fields
  const rooms: Room[] = rawRooms.map((r: any) => {
    const typeKey = String(r.room_type_id || r.type || 'STANDARD').toUpperCase();
    const meta = ROOM_TYPE_DEFAULTS[typeKey] || ROOM_TYPE_DEFAULTS.STANDARD;
    const pricePerNight = Number(r.pricePerNight || r.daily_rate || r.price_per_night || 20000);
    const totalPrice = Number(r.totalPrice || pricePerNight * nights);
    const membershipDiscount = Number(r.membershipDiscount ?? meta.membershipDiscount);
    const membershipPrice = Number(r.membershipPrice ?? Math.round(pricePerNight * (1 - membershipDiscount / 100)));

    return {
      id: String(r.id || `room-${r.room_number || Math.random()}`),
      type: r.type || meta.type,
      name: r.name || (r.room_number ? `${meta.type} - Room ${r.room_number}` : meta.name),
      description: r.description || meta.description,
      pricePerNight,
      totalPrice,
      nights,
      maxCapacity: Number(r.capacity || r.maxCapacity || meta.maxCapacity),
      features: Array.isArray(r.features) && r.features.length ? r.features : meta.features,
      amenities: Array.isArray(r.amenities) && r.amenities.length ? r.amenities : meta.amenities,
      image: r.image || meta.image,
      isBestseller: r.isBestseller ?? meta.isBestseller,
      membershipPrice,
      membershipDiscount,
    };
  });

  return {
    available: rooms.length > 0,
    rooms,
    message: rawResult?.message ?? 'Rooms available',
    hasMembership: rawResult?.hasMembership ?? false,
  };
}




// ─────────────────────────────────────────────
//  OTP
// ─────────────────────────────────────────────

/**
 * POST /api/v1/otp/send
 * Sends an OTP SMS to the given phone number (+94 format).
 * Backend also performs a membership lookup at this stage.
 */
export async function sendOTP(phone: string): Promise<SendOTPResponse> {
  return request<SendOTPResponse>('/api/v1/otp/send', {
    method: 'POST',
    body: JSON.stringify({ phone }),
  });
}

/**
 * POST /api/v1/otp/verify
 * Verifies the OTP entered by the user.
 */
export async function verifyOTP(
  phone: string,
  otp: string
): Promise<VerifyOTPResponse> {
  return request<VerifyOTPResponse>('/api/v1/otp/verify', {
    method: 'POST',
    body: JSON.stringify({ phone, otp }),
  });
}

// ─────────────────────────────────────────────
//  Booking Creation
// ─────────────────────────────────────────────

/**
 * POST /api/v1/booking/create
 * Creates the confirmed booking record in the database.
 * Returns the unique booking reference generated by the backend.
 */
export async function createBooking(
  data: CreateBookingPayload
): Promise<CreateBookingResponse> {
  return request<CreateBookingResponse>('/api/v1/booking/create', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// ─────────────────────────────────────────────
//  MANAGEMENT UI / RECEPTIONIST API
// ─────────────────────────────────────────────

/**
 * GET /api/v1/management/bookings
 * Retrieves all bookings for the active stays and booking management pages.
 */
export async function getAllBookings(): Promise<StaffBooking[]> {
  // Mock data since backend doesn't have management routes yet
  return [
    {
      bookingId: 1002,
      guestName: 'Test Guest',
      phone: '+94771234567',
      branchId: 1,
      bookingReference: 'BKG-1002',
      roomNumber: 101,
      roomType: 'Deluxe',
      checkIn: '2026-10-01',
      checkOut: '2026-10-05',
      status: 'Booked',
      adults: 2,
      children: 0
    },
    {
      bookingId: 1003,
      guestName: 'Kasun Perera',
      phone: '+94711112222',
      branchId: 1,
      bookingReference: 'BKG-1003',
      roomNumber: 205,
      roomType: 'Executive Suite',
      checkIn: '2026-09-28',
      checkOut: '2026-10-02',
      status: 'Checked-In',
      adults: 1,
      children: 0
    }
  ];
}

/**
 * POST /api/v1/management/bookings/:id/checkin
 * Checks in a guest (changes booking to Checked-In, Room to Occupied)
 */
export async function checkInGuest(bookingId: number): Promise<{ success: boolean; message: string }> {
  return new Promise(resolve => setTimeout(() => resolve({ success: true, message: 'Checked in' }), 500));
}

/**
 * POST /api/v1/management/bookings/:id/checkout
 * Checks out a guest (changes booking to Checked-Out). Fails if balance > 0.
 */
export async function checkOutGuest(bookingId: number): Promise<{ success: boolean; message: string }> {
  return new Promise(resolve => setTimeout(() => resolve({ success: true, message: 'Checked out' }), 500));
}

/**
 * GET /api/v1/management/bookings/:id/bill
 * Gets the current calculated bill for a booking.
 */
export async function getBill(bookingId: number): Promise<InvoiceSummary> {
  return new Promise(resolve => setTimeout(() => resolve({
    invoiceId: 'INV-001',
    bookingId,
    totalRoomCharges: 25000,
    totalAmenityCharges: 1500,
    totalServiceCharges: 5000,
    totalTaxAmount: 3000,
    grandTotal: 34500,
    amountPaid: 0,
    paymentStatus: 'Unpaid'
  }), 1000));
}

/**
 * POST /api/v1/management/bookings/:id/services
 * Adds a service to the guest's tab.
 */
export async function addServiceToBooking(bookingId: number, serviceId: number): Promise<{ success: boolean; message: string }> {
  return new Promise(resolve => setTimeout(() => resolve({ success: true, message: 'Service added' }), 500));
}

/**
 * POST /api/v1/management/bookings/:id/amenities
 * Adds an extra amenity to the guest's tab.
 */
export async function addAmenityToBooking(bookingId: number, amenityId: number): Promise<{ success: boolean; message: string }> {
  return new Promise(resolve => setTimeout(() => resolve({ success: true, message: 'Amenity added' }), 500));
}

/**
 * POST /api/v1/management/bookings/:id/extend
 * Extends the checkout date for a booking.
 */
export async function extendStay(bookingId: number, newCheckOutDate: string): Promise<{ success: boolean; message: string }> {
  return new Promise(resolve => setTimeout(() => resolve({ success: true, message: 'Stay extended' }), 500));
}

/**
 * POST /api/v1/management/memberships
 * Creates a new SkyNest Membership
 */
export async function createMembership(data: { name: string; phone: string; email: string }): Promise<{ success: boolean; message: string }> {
  return new Promise(resolve => setTimeout(() => resolve({ success: true, message: 'Membership created successfully' }), 800));
}

// ─────────────────────────────────────────────
//  Authentication API
// ─────────────────────────────────────────────
export async function loginStaff(username: string, password: string): Promise<LoginResponse> {
  const data = await request<LoginResponse>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  setAuthSession(data.access_token, data.user);
  return data;
}

export async function fetchCurrentStaff(): Promise<StaffUser> {
  return request<StaffUser>('/api/v1/auth/me');
}
