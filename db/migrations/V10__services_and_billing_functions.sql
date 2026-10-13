-- Multi-table service charging and checkout stay in PostgreSQL.

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
