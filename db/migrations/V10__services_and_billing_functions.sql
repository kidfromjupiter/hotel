-- V10: Database functions for hotel services, active stays, and billing/invoicing

-- 1. Get all available hotel services from catalogue
CREATE OR REPLACE FUNCTION get_all_services()
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'service_id', sc.service_id,
        'service_name', sc.service_name,
        'day_rate', sc.day_rate,
        'description', COALESCE(sc.description, sc.service_name)
      )
      ORDER BY sc.service_id ASC
    ),
    '[]'::JSONB
  )
  INTO result
  FROM service_catalogue sc;

  RETURN result;
END;
$$;


-- 2. Get active checked-in stays
CREATE OR REPLACE FUNCTION get_active_stays()
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'booking_id', b.booking_id,
        'booking_ref', b.booking_ref,
        'guest_id', b.guest_id,
        'guest_name', COALESCE(g.name, 'Valued Guest'),
        'guest_phone', COALESCE(g.phone_number::TEXT, ''),
        'room_number', b.room_number,
        'branch_id', b.branch_id,
        'room_type_id', COALESCE(rd.room_type_id, 'Standard'),
        'start_date', b.start_date,
        'end_date', b.end_date,
        'booking_status', b.booking_status,
        'is_member', (g.membership_id IS NOT NULL),
        'membership_name', COALESCE(m.membership_name, 'None'),
        'room_discount_percentage', COALESCE(m.room_discount_percentage, 0.0),
        'service_discount_percentage', COALESCE(m.service_discount_percentage, 0.0)
      )
      ORDER BY b.start_date ASC
    ),
    '[]'::JSONB
  )
  INTO result
  FROM booking b
  LEFT JOIN guests g ON b.guest_id = g.guest_id
  LEFT JOIN skynest_membership m ON g.membership_id = m.membership_id
  LEFT JOIN room_details rd ON b.room_number = rd.room_number AND b.branch_id = rd.branch_id
  WHERE b.booking_status ILIKE '%check%' OR b.booking_status ILIKE '%confirm%';

  RETURN result;
END;
$$;


-- 3. Add service charge to a booking
CREATE OR REPLACE FUNCTION add_service_to_booking(
  p_booking_id BIGINT,
  p_service_id INT,
  p_service_dates INT DEFAULT 1
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  v_rate DECIMAL(10,2);
  v_service_name VARCHAR(255);
  v_discount DECIMAL(10,2) := 0.0;
  v_service_total DECIMAL(10,2);
  v_next_log_id INT;
BEGIN
  -- Get service details
  SELECT day_rate, service_name INTO v_rate, v_service_name
  FROM service_catalogue
  WHERE service_id = p_service_id;

  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'message', 'Service not found');
  END IF;

  -- Check for guest membership discount
  SELECT COALESCE(m.service_discount_percentage, 0.0)
  INTO v_discount
  FROM booking b
  JOIN guests g ON b.guest_id = g.guest_id
  LEFT JOIN skynest_membership m ON g.membership_id = m.membership_id
  WHERE b.booking_id = p_booking_id;

  -- Calculate total
  v_service_total := ROUND((v_rate * p_service_dates) * (1.0 - (v_discount / 100.0)), 2);

  -- Next log id
  SELECT COALESCE(MAX(service_log_id), 0) + 1 INTO v_next_log_id FROM service_charges;

  INSERT INTO service_charges (service_log_id, booking_id, service_id, service_dates, service_total)
  VALUES (v_next_log_id, p_booking_id, p_service_id, p_service_dates, v_service_total);

  -- Update billing summary if already exists
  UPDATE billing_summary
  SET total_service_charges = COALESCE(total_service_charges, 0) + v_service_total,
      grand_total = COALESCE(grand_total, 0) + v_service_total
  WHERE booking_id = p_booking_id;

  RETURN jsonb_build_object(
    'success', true,
    'message', 'Service charged successfully',
    'service_log_id', v_next_log_id,
    'booking_id', p_booking_id,
    'service_name', v_service_name,
    'service_dates', p_service_dates,
    'day_rate', v_rate,
    'discount_percentage', v_discount,
    'service_total', v_service_total
  );
END;
$$;


-- 4. Add extra amenity to a booking
CREATE OR REPLACE FUNCTION add_extra_amenity_to_booking(
  p_booking_id BIGINT,
  p_amenity_id INT,
  p_quantity INT DEFAULT 1
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO booking_extra_amenities (booking_id, amenity_id, quantity)
  VALUES (p_booking_id, p_amenity_id, p_quantity)
  ON CONFLICT (booking_id, amenity_id)
  DO UPDATE SET quantity = booking_extra_amenities.quantity + EXCLUDED.quantity;

  RETURN jsonb_build_object(
    'success', true,
    'message', 'Extra amenity added successfully',
    'booking_id', p_booking_id,
    'amenity_id', p_amenity_id,
    'quantity', p_quantity
  );
END;
$$;


-- 5. List all guest invoices / billing summaries
CREATE OR REPLACE FUNCTION get_all_invoices(p_payment_status TEXT DEFAULT NULL)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'invoice_id', bs.invoice_id,
        'booking_id', bs.booking_id,
        'booking_ref', b.booking_ref,
        'guest_name', COALESCE(g.name, 'Valued Guest'),
        'guest_phone', COALESCE(g.phone_number::TEXT, ''),
        'branch_id', b.branch_id,
        'branch_name', COALESCE(br.branch_name, 'Main Branch'),
        'room_number', b.room_number,
        'payment_method', COALESCE(bs.payment_method, 'CREDIT_CARD'),
        'total_room_charges', bs.total_room_charges,
        'total_service_charges', COALESCE(bs.total_service_charges, 0.0),
        'total_tax_amount', COALESCE(bs.total_tax_amount, 0.0),
        'grand_total', bs.grand_total,
        'amount_paid', bs.amount_paid,
        'payment_status', bs.payment_status,
        'outstanding_balance', (bs.grand_total - bs.amount_paid)
      )
      ORDER BY bs.booking_id DESC
    ),
    '[]'::JSONB
  )
  INTO result
  FROM billing_summary bs
  JOIN booking b ON bs.booking_id = b.booking_id
  LEFT JOIN guests g ON b.guest_id = g.guest_id
  LEFT JOIN branches br ON b.branch_id = br.branch_id
  WHERE (
    p_payment_status IS NULL
    OR bs.payment_status ILIKE p_payment_status
  );

  RETURN result;
END;
$$;


-- 6. Process checkout and invoice finalization
CREATE OR REPLACE FUNCTION checkout_booking(
  p_booking_id BIGINT,
  p_payment_method TEXT DEFAULT 'CREDIT_CARD'
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  v_room_num SMALLINT;
  v_branch_id INT;
  v_invoice_id UUID;
  v_grand_total DECIMAL(10,2);
  v_room_charges DECIMAL(10,2);
  v_service_charges DECIMAL(10,2);
  v_tax DECIMAL(10,2);
BEGIN
  -- 1. Find booking
  SELECT room_number, branch_id
  INTO v_room_num, v_branch_id
  FROM booking
  WHERE booking_id = p_booking_id;

  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'message', 'Booking not found');
  END IF;

  -- 2. Update booking status & checkout time
  UPDATE booking
  SET booking_status = 'CHECKED_OUT',
      checked_out_time = CURRENT_TIME
  WHERE booking_id = p_booking_id;

  -- 3. Release room status back to AVAILABLE
  UPDATE room_details
  SET room_status = 'AVAILABLE'
  WHERE room_number = v_room_num AND branch_id = v_branch_id;

  -- 4. Check or create billing summary
  SELECT invoice_id, grand_total, total_room_charges, total_service_charges, total_tax_amount
  INTO v_invoice_id, v_grand_total, v_room_charges, v_service_charges, v_tax
  FROM billing_summary
  WHERE booking_id = p_booking_id;

  IF v_invoice_id IS NULL THEN
    v_invoice_id := gen_random_uuid();
    v_room_charges := 50000.0;
    SELECT COALESCE(SUM(service_total), 0.0) INTO v_service_charges FROM service_charges WHERE booking_id = p_booking_id;
    v_tax := ROUND((v_room_charges + v_service_charges) * 0.10, 2);
    v_grand_total := v_room_charges + v_service_charges + v_tax;

    INSERT INTO billing_summary (
      invoice_id, payment_method, booking_id, total_room_charges,
      total_service_charges, total_tax_amount, grand_total, amount_paid, payment_status
    ) VALUES (
      v_invoice_id, p_payment_method, p_booking_id, v_room_charges,
      v_service_charges, v_tax, v_grand_total, v_grand_total, 'PAID'
    );
  ELSE
    UPDATE billing_summary
    SET payment_status = 'PAID',
        payment_method = p_payment_method,
        amount_paid = grand_total
    WHERE invoice_id = v_invoice_id;
  END IF;

  -- 5. Record transaction
  INSERT INTO transactions (transaction_id, invoice_id, payment_date, amount, payment_method)
  VALUES (gen_random_uuid(), v_invoice_id, CURRENT_TIMESTAMP, v_grand_total, p_payment_method);

  RETURN jsonb_build_object(
    'success', true,
    'message', 'Booking checked out successfully',
    'booking_id', p_booking_id,
    'invoice_id', v_invoice_id,
    'payment_status', 'PAID',
    'grand_total', v_grand_total,
    'amount_paid', v_grand_total
  );
END;
$$;
