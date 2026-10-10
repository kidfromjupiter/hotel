import type {
  AvailabilityPayload,
  AvailabilityResponse,
  AmenitiesResponse,
  SendOTPResponse,
  VerifyOTPResponse,
  CreateBookingPayload,
  CreateBookingResponse,
  StaffBooking,
  BookingStatus,
  GuestProfile,
  ServiceCatalogueItem,
  InvoiceSummary
} from './types';

const BASE_URL = typeof window !== 'undefined' ? (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000') : (process.env.INTERNAL_API_URL ?? 'http://backend:8000');

// ─────────────────────────────────────────────
//  Generic request helper
// ─────────────────────────────────────────────
async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const headers: HeadersInit = { 'Content-Type': 'application/json' };

  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('guest_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { ...headers, ...(options?.headers || {}) },
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
    amenities: [
      { id: 'a1', name: 'Air Conditioning', description: 'Climate control', price: 0, icon: '❄️' },
      { id: 'a2', name: 'Free High-Speed Wi-Fi', description: 'Unlimited access', price: 0, icon: '📶' }
    ],
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
    amenities: [
      { id: 'a1', name: 'Air Conditioning', description: 'Climate control', price: 0, icon: '❄️' },
      { id: 'a2', name: 'Free High-Speed Wi-Fi', description: 'Unlimited access', price: 0, icon: '📶' },
      { id: 'a3', name: 'Minibar', description: 'Fully stocked minibar', price: 0, icon: '🍷' },
      { id: 'a4', name: '24/7 Room Service', description: 'Available anytime', price: 0, icon: '🛎️' }
    ],
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
 * POST /api/v1/rooms/availability
 * Checks room availability for the given branch, dates, and guest count.
 * Returns real available rooms from the backend with prices and calculated totals.
 */
export async function checkAvailability(
  data: AvailabilityPayload
): Promise<AvailabilityResponse> {
  const params = new URLSearchParams();

  if (data.checkIn != null) params.set('check_in', data.checkIn);
  if (data.checkOut != null) params.set('check_out', data.checkOut);
  if (data.adults != null) params.set('adults', String(data.adults));
  if (data.children != null) params.set('children', String(data.children));
  if (data.branch != null) params.set('branch', data.branch);

  const query = params.toString();
  const url = `/api/v1/rooms${query ? `?${query}` : ''}`;

  // Backend returns a raw array of rooms; transform it into AvailabilityResponse shape
  const raw = await request<Array<{
    room_number: number;
    room_type_id: string;
    branch_id: number;
    branch_name: string;
    daily_rate: number;
    price_per_night: number;
    capacity: number;
    room_status: string;
  }>>(url, { method: 'GET' });

  const hasMembership = typeof window !== 'undefined' ? !!localStorage.getItem('guest_token') : false;

  const rooms: AvailabilityResponse['rooms'] = raw.map(r => {
    const pricePerNight = r.price_per_night ?? r.daily_rate;
    const membershipDiscount = 15; // 15% off for members
    const membershipPrice = Math.round(pricePerNight * (1 - membershipDiscount / 100));

    return {
      id: String(r.room_number),
      roomNumber: r.room_number,
      type: r.room_type_id,
      name: r.room_type_id,
      description: '',
      branchId: r.branch_id,
      branchName: r.branch_name,
      pricePerNight,
      membershipPrice,
      membershipDiscount,
      capacity: r.capacity,
      maxCapacity: r.capacity,
      status: r.room_status,
      totalPrice: 0,
      nights: 0,
      features: [],
      amenities: [],
      image: '',
    };
  });

  return {
    available: rooms.length > 0,
    rooms,
    hasMembership,
    message: rooms.length === 0 ? 'No rooms available for the selected dates.' : undefined,
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
  return request<CreateBookingResponse>('/api/v1/bookings/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * GET /api/v1/bookings/?status=Checked-In
 * Fetches all guests who are currently checked in (Active Stays).
 */
export async function getActiveStays(): Promise<any[]> {
  return request<any[]>('/api/v1/bookings/?status=Checked-In', {
    method: 'GET',
  });
}

/**
 * POST /api/v1/bookings/{booking_id}/services
 * Adds a service to the guest's tab.
 */
export async function addServiceToTab(bookingId: number, serviceName: string, serviceTotal: number): Promise<any> {
  return request<any>(`/api/v1/bookings/${bookingId}/services`, {
    method: 'POST',
    body: JSON.stringify({
      service_name: serviceName,
      service_total: serviceTotal,
      service_dates: 1
    }),
  });
}

/**
 * GET /api/v1/booking/
 * Gets the reservations for the authenticated guest
 */
export async function getMyBookings(): Promise<StaffBooking[]> {
  const raw = await request<Array<{
    booking_id: number;
    guest_name: string;
    room_number: number;
    branch_name: string;
    booking_status: string;
    start_date: string;
    end_date: string;
  }>>('/api/v1/booking/');

  return raw.map(b => ({
    bookingId: b.booking_id,
    guestName: b.guest_name,
    phone: '',
    branchId: 0,
    bookingReference: `BKG-${b.booking_id}`,
    roomNumber: b.room_number,
    roomType: '',
    checkIn: b.start_date,
    checkOut: b.end_date,
    status: b.booking_status as BookingStatus,
    adults: 0,
    children: 0,
  }));
}

// ─────────────────────────────────────────────
//  MANAGEMENT UI / RECEPTIONIST API
// ─────────────────────────────────────────────

/**
 * GET /api/v1/private/bookings/admin-reservations
 */
export async function getAdminReservationsList(status?: string): Promise<any[]> {
  const url = status 
    ? `/api/v1/private/bookings/admin-reservations?status=${encodeURIComponent(status)}`
    : '/api/v1/private/bookings/admin-reservations';
  return request<any[]>(url, { method: 'GET' });
}

/**
 * GET /api/v1/bookings/
 * Retrieves all bookings. Maps backend BookingListItem → frontend StaffBooking.
 */
export async function getAllBookings(): Promise<StaffBooking[]> {
  const raw = await request<Array<{
    booking_id: number;
    guest_name: string;
    room_number: number;
    branch_name: string;
    booking_status: string;
    start_date: string;
    end_date: string;
  }>>('/api/v1/bookings/');

  return raw.map(b => ({
    bookingId: b.booking_id,
    guestName: b.guest_name,
    phone: '',
    branchId: 0,
    bookingReference: `BKG-${b.booking_id}`,
    roomNumber: b.room_number,
    roomType: '',
    checkIn: b.start_date,
    checkOut: b.end_date,
    status: b.booking_status as BookingStatus,
    adults: 0,
    children: 0,
  }));
}

/**
 * GET /api/v1/bookings/{id}
 * Gets full booking details including services and invoice.
 */
export async function getBookingDetail(bookingId: number): Promise<InvoiceSummary> {
  const b = await request<{
    booking_id: number;
    booking_status: string;
    service_charges: Array<{ service_name: string; service_total: number }>;
    invoice_status: string;
    grand_total: number;
    amount_paid: number;
  }>(`/api/v1/bookings/${bookingId}`);

  const totalServiceCharges = b.service_charges.reduce((sum, s) => sum + s.service_total, 0);

  return {
    invoiceId: `INV-${bookingId}`,
    bookingId: b.booking_id,
    totalRoomCharges: b.grand_total - totalServiceCharges,
    totalAmenityCharges: 0,
    totalServiceCharges,
    totalTaxAmount: 0,
    grandTotal: b.grand_total,
    amountPaid: b.amount_paid,
    paymentStatus: b.invoice_status as 'Paid' | 'Partial' | 'Unpaid',
  };
}

/**
 * POST /api/v1/bookings/{id}/check-in
 * Checks in a guest (changes booking to Checked-In, Room to Occupied)
 */
export async function checkInGuest(bookingId: number): Promise<{ success: boolean; message: string }> {
  try {
    await request(`/api/v1/bookings/${bookingId}/check-in`, { method: 'POST' });
    return { success: true, message: 'Guest checked in successfully' };
  } catch (e: any) {
    return { success: false, message: e.message ?? 'Check-in failed' };
  }
}

/**
 * POST /api/v1/bookings/{id}/check-out
 * Checks out a guest. Enforces full invoice payment before checkout.
 */
export async function checkOutGuest(bookingId: number): Promise<{ success: boolean; message: string }> {
  try {
    await request(`/api/v1/bookings/${bookingId}/check-out`, { method: 'POST' });
    return { success: true, message: 'Guest checked out successfully' };
  } catch (e: any) {
    return { success: false, message: e.message ?? 'Check-out failed' };
  }
}

/**
 * GET /api/v1/bookings/{id}/bill  (uses getBookingDetail internally)
 */
export async function getBill(bookingId: number): Promise<InvoiceSummary> {
  return getBookingDetail(bookingId);
}

/**
 * POST /api/v1/bookings/{id}/cancel
 */
export async function cancelBooking(bookingId: number): Promise<{ success: boolean; message: string }> {
  try {
    await request(`/api/v1/bookings/${bookingId}/cancel`, { method: 'POST' });
    return { success: true, message: 'Booking cancelled' };
  } catch (e: any) {
    return { success: false, message: e.message ?? 'Cancellation failed' };
  }
}

// These endpoints are not yet implemented in the backend — kept as stubs
export async function addServiceToBooking(bookingId: number, serviceName: string, serviceTotal: number, serviceDates: number = 1): Promise<{ success: boolean; message: string }> {
  try {
    await request(`/api/v1/bookings/${bookingId}/services`, { 
      method: 'POST',
      body: JSON.stringify({ service_name: serviceName, service_total: serviceTotal, service_dates: serviceDates })
    });
    return { success: true, message: 'Service added successfully' };
  } catch (e: any) {
    return { success: false, message: e.message ?? 'Failed to add service' };
  }
}

export async function addAmenityToBooking(bookingId: number, amenityId: number): Promise<{ success: boolean; message: string }> {
  return new Promise(resolve => setTimeout(() => resolve({ success: true, message: 'Amenity added' }), 500));
}

export async function extendStay(bookingId: number, newCheckOutDate: string): Promise<{ success: boolean; message: string }> {
  try {
    await request(`/api/v1/bookings/${bookingId}/extend`, { 
      method: 'POST',
      body: JSON.stringify({ new_checkout_date: newCheckOutDate })
    });
    return { success: true, message: 'Stay extended successfully' };
  } catch (e: any) {
    return { success: false, message: e.message ?? 'Failed to extend stay' };
  }
}

/**
 * POST /api/v1/guests/memberships
 * Creates a new SkyNest Membership
 */
export async function createMembership(data: { name: string; phone: string; email: string }): Promise<{ success: boolean; message: string }> {
  try {
    await request(`/api/v1/guests/memberships`, { 
      method: 'POST',
      body: JSON.stringify(data)
    });
    return { success: true, message: 'Guest successfully enrolled in SkyNest Membership!' };
  } catch (e: any) {
    return { success: false, message: e.message ?? 'Failed to enroll member' };
  }
}

// ─────────────────────────────────────────────
//  ADMIN API
// ─────────────────────────────────────────────

/**
 * GET /api/v1/rooms/all
 * Returns all rooms in the hotel.
 */
export async function getAllRooms(): Promise<any[]> {
  return request('/api/v1/rooms/all');
}

/**
 * GET /api/v1/branches/
 * Returns all hotel branches.
 */
export async function getBranches(): Promise<Array<{ branch_id: number; branch_name: string }>> {
  return request('/api/v1/branches/');
}

/**
 * GET /api/v1/reports/monthly-revenue?year=YYYY
 * Returns monthly revenue breakdown per branch for a given year.
 */
export async function getMonthlyRevenue(year: number): Promise<{
  year: number;
  data: Array<{ branch_name: string; month: string; room_revenue: number; service_revenue: number; total_revenue: number }>;
}> {
  return request(`/api/v1/reports/monthly-revenue?year=${year}`);
}

/**
 * GET /api/v1/reports/occupancy?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
 * Returns occupancy rate per branch for a given period.
 */
export async function getOccupancyReport(startDate: string, endDate: string): Promise<{
  period: { start_date: string; end_date: string };
  branches: Array<{ branch_name: string; total_rooms: number; occupied_nights: number; total_possible_nights: number; occupancy_rate_percent: number }>;
}> {
  return request(`/api/v1/reports/occupancy?start_date=${startDate}&end_date=${endDate}`);
}

/**
 * GET /api/v1/services/
 * Returns all services.
 */
export async function getServices(): Promise<Array<{ service_id: number; service_name: string; day_rate: number; description: string }>> {
  return request('/api/v1/services/');
}

/**
 * GET /api/v1/guests/
 * Returns all guests.
 */
export async function getGuests(): Promise<Array<{ guest_id: number; name: string; national_id: string; phone_number: string; membership_id: number | null }>> {
  return request('/api/v1/guests/');
}

/**
 * GET /api/v1/amenities
 * Returns all amenities.
 */
export async function getAmenities(): Promise<Array<{ id: number; name: string; price: number }>> {
  return request('/api/v1/amenities');
}
