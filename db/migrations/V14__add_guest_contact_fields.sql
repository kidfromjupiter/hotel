-- V14: Add email to guests, special_requests to booking, and update guest lookup functions
ALTER TABLE guests ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE booking ADD COLUMN IF NOT EXISTS special_requests TEXT;

-- Update get_all_guests to include email
CREATE OR REPLACE FUNCTION get_all_guests(p_search TEXT DEFAULT NULL)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'guest_id', g.guest_id,
        'name', g.name,
        'email', g.email,
        'national_id', g.national_id,
        'phone_number', g.phone_number::TEXT,
        'membership_id', g.membership_id,
        'membership_name', COALESCE(m.membership_name, 'None'),
        'room_discount_percentage', COALESCE(m.room_discount_percentage, 0.0),
        'service_discount_percentage', COALESCE(m.service_discount_percentage, 0.0)
      )
      ORDER BY g.guest_id ASC
    ),
    '[]'::JSONB
  )
  INTO result
  FROM guests g
  LEFT JOIN skynest_membership m ON g.membership_id = m.membership_id
  WHERE (
    p_search IS NULL
    OR g.name ILIKE ('%' || p_search || '%')
    OR g.email ILIKE ('%' || p_search || '%')
    OR g.national_id ILIKE ('%' || p_search || '%')
    OR g.phone_number::TEXT ILIKE ('%' || p_search || '%')
  );

  RETURN result;
END;
$$;

-- Update get_guest_by_phone to include email
CREATE OR REPLACE FUNCTION get_guest_by_phone(p_phone TEXT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  v_digits TEXT;
  v_phone_int INT;
  result JSONB;
BEGIN
  v_digits := REGEXP_REPLACE(p_phone, '[^0-9]', '', 'g');
  IF v_digits LIKE '94%' THEN
    v_digits := SUBSTRING(v_digits FROM 3);
  ELSIF v_digits LIKE '0%' THEN
    v_digits := SUBSTRING(v_digits FROM 2);
  END IF;

  BEGIN
    v_phone_int := v_digits::INT;
  EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
  END;

  SELECT jsonb_build_object(
    'guest_id', g.guest_id,
    'name', g.name,
    'email', g.email,
    'national_id', g.national_id,
    'phone_number', g.phone_number::TEXT,
    'membership_id', g.membership_id,
    'has_membership', (g.membership_id IS NOT NULL),
    'membership_name', COALESCE(m.membership_name, 'None'),
    'room_discount_percentage', COALESCE(m.room_discount_percentage, 0.0),
    'service_discount_percentage', COALESCE(m.service_discount_percentage, 0.0)
  )
  INTO result
  FROM guests g
  LEFT JOIN skynest_membership m ON g.membership_id = m.membership_id
  WHERE g.phone_number = v_phone_int
  LIMIT 1;

  RETURN result;
END;
$$;

-- Update get_guest_by_id to include email
CREATE OR REPLACE FUNCTION get_guest_by_id(p_guest_id INT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT jsonb_build_object(
    'guest_id', g.guest_id,
    'name', g.name,
    'email', g.email,
    'national_id', g.national_id,
    'phone_number', g.phone_number::TEXT,
    'membership_id', g.membership_id,
    'has_membership', (g.membership_id IS NOT NULL),
    'membership_name', COALESCE(m.membership_name, 'None'),
    'room_discount_percentage', COALESCE(m.room_discount_percentage, 0.0),
    'service_discount_percentage', COALESCE(m.service_discount_percentage, 0.0)
  )
  INTO result
  FROM guests g
  LEFT JOIN skynest_membership m ON g.membership_id = m.membership_id
  WHERE g.guest_id = p_guest_id;

  RETURN result;
END;
$$;

-- Update get_booking_by_id to include email, phone, national_id, and special_requests
CREATE OR REPLACE FUNCTION get_booking_by_id(p_booking_id BIGINT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT jsonb_build_object(
    'booking_id', bk.booking_id,
    'guest_id', bk.guest_id,
    'guest_name', COALESCE(g.name, 'Guest'),
    'guest_email', g.email,
    'guest_phone', g.phone_number::TEXT,
    'national_id', g.national_id,
    'special_requests', bk.special_requests,
    'room_number', bk.room_number,
    'branch_id', bk.branch_id,
    'branch_name', INITCAP(COALESCE(b.branch_name, 'Colombo')),
    'room_type_id', COALESCE(rd.room_type_id, 'STANDARD'),
    'booking_status', bk.booking_status,
    'start_date', bk.start_date,
    'end_date', bk.end_date,
    'checked_in_time', bk.checked_in_time::TEXT,
    'checked_out_time', bk.checked_out_time::TEXT,
    'adult_count', bk.adult_count,
    'children_count', bk.children_count,
    'grand_total', COALESCE(bs.grand_total, 0.0),
    'amount_paid', COALESCE(bs.amount_paid, 0.0),
    'invoice_status', COALESCE(bs.payment_status, 'UNPAID'),
    'service_charges', COALESCE(
      (
        SELECT jsonb_agg(
          jsonb_build_object(
            'service_name', sc_cat.service_name,
            'service_dates', sc.service_dates,
            'service_total', sc.service_total
          )
        )
        FROM service_charges sc
        LEFT JOIN service_catalogue sc_cat ON sc.service_id = sc_cat.service_id
        WHERE sc.booking_id = bk.booking_id
      ),
      '[]'::JSONB
    )
  )
  INTO result
  FROM booking bk
  LEFT JOIN guests g ON bk.guest_id = g.guest_id
  LEFT JOIN branches b ON bk.branch_id = b.branch_id
  LEFT JOIN room_details rd ON bk.room_number = rd.room_number AND bk.branch_id = rd.branch_id
  LEFT JOIN billing_summary bs ON bk.booking_id = bs.booking_id
  WHERE bk.booking_id = p_booking_id;

  RETURN result;
END;
$$;

-- Update get_all_bookings to include email, phone, national_id, and special_requests
CREATE OR REPLACE FUNCTION get_all_bookings(
  p_branch_id INTEGER DEFAULT NULL::INTEGER,
  p_guest_id INTEGER DEFAULT NULL::INTEGER,
  p_status CHARACTER VARYING DEFAULT NULL::CHARACTER VARYING,
  p_start_date DATE DEFAULT NULL::DATE,
  p_end_date DATE DEFAULT NULL::DATE
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'booking_id', bk.booking_id,
        'guest_id', bk.guest_id,
        'guest_name', COALESCE(g.name, 'Guest'),
        'guest_email', g.email,
        'guest_phone', g.phone_number::TEXT,
        'national_id', g.national_id,
        'special_requests', bk.special_requests,
        'room_number', bk.room_number,
        'branch_id', bk.branch_id,
        'branch_name', INITCAP(COALESCE(b.branch_name, 'Colombo')),
        'room_type_id', rd.room_type_id,
        'booking_status', bk.booking_status,
        'start_date', bk.start_date,
        'end_date', bk.end_date,
        'checked_in_time', bk.checked_in_time::TEXT,
        'checked_out_time', bk.checked_out_time::TEXT,
        'adult_count', bk.adult_count,
        'children_count', bk.children_count,
        'grand_total', COALESCE(bs.grand_total, 0.0),
        'amount_paid', COALESCE(bs.amount_paid, 0.0),
        'invoice_status', COALESCE(bs.payment_status, 'UNPAID'),
        'is_member', (g.membership_id IS NOT NULL)
      )
      ORDER BY bk.booking_id DESC
    ),
    '[]'::JSONB
  )
  INTO result
  FROM booking bk
  LEFT JOIN guests g ON bk.guest_id = g.guest_id
  LEFT JOIN branches b ON bk.branch_id = b.branch_id
  LEFT JOIN room_details rd ON bk.room_number = rd.room_number AND bk.branch_id = rd.branch_id
  LEFT JOIN billing_summary bs ON bk.booking_id = bs.booking_id
  WHERE (p_branch_id IS NULL OR bk.branch_id = p_branch_id)
    AND (p_guest_id IS NULL OR bk.guest_id = p_guest_id)
    AND (p_status IS NULL OR LOWER(bk.booking_status) = LOWER(p_status))
    AND (p_start_date IS NULL OR bk.start_date >= p_start_date)
    AND (p_end_date IS NULL OR bk.end_date <= p_end_date);

  RETURN result;
END;
$$;
