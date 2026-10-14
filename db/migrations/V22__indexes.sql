-- 1. Booking table indexes
-- Room availability and  double-booking trigger lookups
CREATE INDEX IF NOT EXISTS idx_booking_branch_room_dates
    ON booking (branch_id, room_number, start_date, end_date);

-- Foreign key for guest's bookings
CREATE INDEX IF NOT EXISTS idx_booking_guest_id
    ON booking (guest_id);

-- Expression index for case-insensitive status lookups in booking_repo
CREATE INDEX IF NOT EXISTS idx_booking_status_lower
    ON booking (LOWER(booking_status));

-- 2. OTP log table indexes
-- Verification query with reverse otp_id ordering (matches ORDER BY otp_id DESC LIMIT 1)
CREATE INDEX IF NOT EXISTS idx_otp_log_verify
    ON otp_log (phone_number, otp_code, otp_status, otp_id DESC);

-- Lookup phone by verified OTP
CREATE INDEX IF NOT EXISTS idx_otp_log_verified_lookup
    ON otp_log (otp_code, otp_status, otp_id DESC);

-- 3. High-traffic tables joined with booking
CREATE INDEX IF NOT EXISTS idx_billing_summary_booking_id
    ON billing_summary (booking_id);

CREATE INDEX IF NOT EXISTS idx_service_charges_booking_id
    ON service_charges (booking_id);
