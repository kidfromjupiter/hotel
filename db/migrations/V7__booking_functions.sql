-- V5: Database functions for bookings and room availability calculation

-- 1. Enhanced get_available_rooms function
CREATE OR REPLACE FUNCTION get_available_rooms(
  p_check_in DATE,
  p_check_out DATE,
  p_branch TEXT,
  p_children INTEGER,
  p_adults INTEGER
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
        'room_number', r.room_number,
        'branch_id', r.branch_id,
        'branch_name', INITCAP(b.branch_name),
        'room_type_id', r.room_type_id,
        'room_status', r.room_status,
        'capacity', r.capacity,
        'price_per_night', rt.daily_rate,
        'daily_rate', rt.daily_rate
      )
      ORDER BY r.room_number
    ),
    '[]'::JSONB
  )
  INTO result 
  FROM room_details r
  JOIN branches b ON r.branch_id = b.branch_id
  LEFT JOIN room_types rt ON r.room_type_id = rt.room_type_id
  WHERE (p_branch IS NULL OR LOWER(b.branch_name) = LOWER(p_branch))
    AND (r.capacity >= (COALESCE(p_adults, 0) + COALESCE(p_children, 0)))
    AND r.room_status != 'MAINTENANCE'
    AND NOT EXISTS (
      SELECT 1 
      FROM booking bk
      WHERE bk.room_number = r.room_number
        AND bk.branch_id = r.branch_id
        AND bk.booking_status != 'Cancelled'
        AND bk.start_date < p_check_out
        AND bk.end_date > p_check_in
    );

  RETURN result;
END;
$$;


-- 2. Get all bookings with filtering
CREATE OR REPLACE FUNCTION get_all_bookings(
  p_branch_id INT DEFAULT NULL,
  p_guest_id INT DEFAULT NULL,
  p_status TEXT DEFAULT NULL,
  p_start_date DATE DEFAULT NULL,
  p_end_date DATE DEFAULT NULL
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
        'invoice_status', COALESCE(bs.payment_status, 'UNPAID')
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


-- 3. Get single booking by ID with full service charge breakdown
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


-- 4. Update booking status and check-in / check-out times
CREATE OR REPLACE FUNCTION update_booking_status(
  p_booking_id BIGINT,
  p_status TEXT,
  p_check_in_time TIME DEFAULT NULL,
  p_check_out_time TIME DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE booking
  SET 
    booking_status = p_status,
    checked_in_time = COALESCE(p_check_in_time, checked_in_time),
    checked_out_time = COALESCE(p_check_out_time, checked_out_time)
  WHERE booking_id = p_booking_id;

  RETURN get_booking_by_id(p_booking_id);
END;
$$;


-- 5. Create new booking transactionally
CREATE OR REPLACE FUNCTION create_booking(
  p_booking_id BIGINT,
  p_room_number SMALLINT,
  p_branch_id INT,
  p_guest_id INT,
  p_booking_status VARCHAR(50),
  p_start_date DATE,
  p_end_date DATE,
  p_adult_count INT,
  p_children_count INT,
  p_grand_total NUMERIC DEFAULT 0.0,
  p_amount_paid NUMERIC DEFAULT 0.0,
  p_payment_method VARCHAR(50) DEFAULT 'CREDIT_CARD'
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  v_invoice_id UUID;
BEGIN
  INSERT INTO booking (
    booking_id,
    room_number,
    branch_id,
    guest_id,
    booking_status,
    start_date,
    end_date,
    adult_count,
    children_count
  ) VALUES (
    p_booking_id,
    p_room_number,
    p_branch_id,
    p_guest_id,
    p_booking_status,
    p_start_date,
    p_end_date,
    p_adult_count,
    p_children_count
  );

  v_invoice_id := gen_random_uuid();
  INSERT INTO billing_summary (
    invoice_id,
    payment_method,
    booking_id,
    total_room_charges,
    total_service_charges,
    total_tax_amount,
    grand_total,
    amount_paid,
    payment_status
  ) VALUES (
    v_invoice_id,
    p_payment_method,
    p_booking_id,
    p_grand_total,
    0.0,
    0.0,
    p_grand_total,
    p_amount_paid,
    CASE WHEN p_amount_paid >= p_grand_total AND p_grand_total > 0 THEN 'PAID' ELSE 'UNPAID' END
  );

  RETURN get_booking_by_id(p_booking_id);
END;
$$;
