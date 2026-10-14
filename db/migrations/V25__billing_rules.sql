CREATE OR REPLACE FUNCTION create_booking(
  p_booking_id BIGINT, p_room_number SMALLINT, p_branch_id INT, p_guest_id INT,
  p_booking_status VARCHAR(50), p_start_date DATE, p_end_date DATE,
  p_adult_count INT, p_children_count INT, p_grand_total NUMERIC DEFAULT 0.0,
  p_amount_paid NUMERIC DEFAULT 0.0, p_payment_method VARCHAR(50) DEFAULT 'CREDIT_CARD'
) RETURNS JSONB LANGUAGE plpgsql AS $$
DECLARE v_invoice UUID; v_rate NUMERIC(10,2); v_discount NUMERIC(5,2);
        v_tax_rate NUMERIC(5,2); v_room NUMERIC(10,2); v_tax NUMERIC(10,2);
BEGIN
  IF p_amount_paid <> 0 THEN RAISE EXCEPTION 'Payments require a checked-in booking'; END IF;
  IF p_booking_status IS DISTINCT FROM 'CONFIRMED' THEN RAISE EXCEPTION 'New bookings must be confirmed'; END IF;
  SELECT rt.daily_rate, COALESCE(m.room_discount_percentage, 0)
  INTO v_rate, v_discount
  FROM room_details rd JOIN room_types rt ON rt.room_type_id = rd.room_type_id
  JOIN guests g ON g.guest_id = p_guest_id
  LEFT JOIN skynest_membership m ON m.membership_id = g.membership_id
  WHERE rd.branch_id = p_branch_id AND rd.room_number = p_room_number;
  IF NOT FOUND THEN RAISE EXCEPTION 'Room or guest not found'; END IF;
  SELECT COALESCE(SUM(tax_percentage), 0) INTO v_tax_rate FROM tax_policies WHERE active;
  v_room := ROUND((p_end_date - p_start_date) * v_rate * (1 - v_discount / 100), 2);
  v_tax := ROUND(v_room * v_tax_rate / 100, 2);
  INSERT INTO booking (booking_id, booking_ref, room_number, branch_id, guest_id,
      booking_status, start_date, end_date, adult_count, children_count,
      nightly_rate, room_discount_percentage)
  VALUES (p_booking_id, 'SKN-' || p_booking_id, p_room_number, p_branch_id, p_guest_id,
      p_booking_status, p_start_date, p_end_date, p_adult_count, p_children_count,
      v_rate, v_discount);
  v_invoice := gen_random_uuid();
  INSERT INTO billing_summary (invoice_id, payment_method, booking_id,
      total_room_charges, total_service_charges, total_tax_amount,
      grand_total, amount_paid, payment_status, tax_rate)
  VALUES (v_invoice, p_payment_method, p_booking_id, v_room, 0, v_tax,
      v_room + v_tax, 0, 'UNPAID', v_tax_rate);
  INSERT INTO invoice_taxes (invoice_id, tax_id, calculated_amount)
  SELECT v_invoice, tax_id, ROUND(v_room * tax_percentage / 100, 2)
  FROM tax_policies WHERE active;
  RETURN jsonb_build_object('booking_id', p_booking_id,
      'booking_ref', 'SKN-' || p_booking_id::TEXT, 'grand_total', v_room + v_tax);
END;
$$;

CREATE OR REPLACE FUNCTION guard_booking_status_change()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE v_status TEXT; v_total NUMERIC(10,2); v_paid NUMERIC(10,2);
BEGIN
  IF NEW.booking_status = OLD.booking_status THEN RETURN NEW; END IF;
  IF OLD.booking_status = 'CONFIRMED' AND NEW.booking_status = 'CHECKED_IN' THEN
    SELECT room_status INTO v_status FROM room_details
    WHERE branch_id = NEW.branch_id AND room_number = NEW.room_number FOR UPDATE;
    IF v_status <> 'AVAILABLE' THEN RAISE EXCEPTION 'Room is not available for check-in'; END IF;
    UPDATE room_details SET room_status = 'OCCUPIED'
    WHERE branch_id = NEW.branch_id AND room_number = NEW.room_number;
  ELSIF OLD.booking_status = 'CHECKED_IN' AND NEW.booking_status = 'CHECKED_OUT' THEN
    SELECT grand_total, amount_paid INTO v_total, v_paid
    FROM billing_summary WHERE booking_id = NEW.booking_id FOR UPDATE;
    IF NOT FOUND OR v_paid < v_total THEN RAISE EXCEPTION 'Checkout requires full payment'; END IF;
    UPDATE room_details SET room_status = 'AVAILABLE'
    WHERE branch_id = NEW.branch_id AND room_number = NEW.room_number;
  ELSIF NOT (OLD.booking_status = 'CONFIRMED' AND NEW.booking_status = 'CANCELLED') THEN
    RAISE EXCEPTION 'Invalid booking status transition';
  END IF;
  RETURN NEW;
END;
$$;
CREATE TRIGGER booking_status_guard BEFORE UPDATE OF booking_status ON booking
FOR EACH ROW EXECUTE FUNCTION guard_booking_status_change();

DROP FUNCTION add_service_to_booking(BIGINT, INT, INT);
CREATE FUNCTION add_service_to_booking(
  p_booking_id BIGINT, p_service_id INT, p_quantity INT DEFAULT 1,
  p_usage_date DATE DEFAULT CURRENT_DATE
) RETURNS JSONB LANGUAGE plpgsql AS $$
DECLARE v_rate NUMERIC(10,2); v_discount NUMERIC(5,2); v_total NUMERIC(10,2);
        v_id INT; v_start DATE; v_end DATE; v_status TEXT;
BEGIN
  SELECT start_date, end_date, booking_status INTO v_start, v_end, v_status
  FROM booking WHERE booking_id = p_booking_id FOR UPDATE;
  IF NOT FOUND OR v_status <> 'CHECKED_IN' THEN
    RETURN jsonb_build_object('success', false, 'message', 'A checked-in booking is required');
  END IF;
  IF p_quantity IS NULL OR p_quantity <= 0 OR p_usage_date < v_start OR p_usage_date >= v_end THEN
    RETURN jsonb_build_object('success', false, 'message', 'Invalid service quantity or usage date');
  END IF;
  SELECT sc.day_rate, COALESCE(m.service_discount_percentage, 0)
  INTO v_rate, v_discount FROM service_catalogue sc
  JOIN booking b ON b.booking_id = p_booking_id
  JOIN guests g ON g.guest_id = b.guest_id
  LEFT JOIN skynest_membership m ON m.membership_id = g.membership_id
  WHERE sc.service_id = p_service_id;
  IF NOT FOUND THEN RETURN jsonb_build_object('success', false, 'message', 'Service not found'); END IF;
  v_total := ROUND(v_rate * p_quantity * (1 - v_discount / 100), 2);
  INSERT INTO service_charges (booking_id, service_id, quantity, usage_date,
      unit_price, discount_percentage, service_total)
  VALUES (p_booking_id, p_service_id, p_quantity, p_usage_date,
      v_rate, v_discount, v_total) RETURNING service_log_id INTO v_id;
  PERFORM recalculate_booking_bill(p_booking_id);
  RETURN jsonb_build_object('success', true, 'service_log_id', v_id,
      'booking_id', p_booking_id, 'quantity', p_quantity,
      'usage_date', p_usage_date, 'unit_price', v_rate, 'service_total', v_total);
END;
$$;

CREATE OR REPLACE FUNCTION extend_booking_stay(p_booking_id BIGINT, p_new_end_date DATE)
RETURNS JSONB LANGUAGE plpgsql AS $$
DECLARE v_start DATE; v_old_end DATE; v_status TEXT; v_invoice UUID;
        v_old_room NUMERIC(10,2); v_new_room NUMERIC(10,2); v_total NUMERIC(10,2);
        v_payment_status TEXT;
BEGIN
  SELECT start_date, end_date, booking_status INTO v_start, v_old_end, v_status
  FROM booking WHERE booking_id = p_booking_id FOR UPDATE;
  IF NOT FOUND THEN RETURN jsonb_build_object('success', false, 'error_code', 'NOT_FOUND', 'message', 'Booking not found.'); END IF;
  IF v_status <> 'CHECKED_IN' THEN RETURN jsonb_build_object('success', false, 'error_code', 'INVALID_STATUS', 'message', 'Only checked-in bookings can be extended.'); END IF;
  IF p_new_end_date <= v_old_end THEN RETURN jsonb_build_object('success', false, 'error_code', 'INVALID_DATE', 'message', 'The new check-out date must be later.'); END IF;
  SELECT invoice_id, total_room_charges INTO v_invoice, v_old_room
  FROM billing_summary WHERE booking_id = p_booking_id FOR UPDATE;
  IF NOT FOUND THEN RETURN jsonb_build_object('success', false, 'error_code', 'BILLING_NOT_FOUND', 'message', 'Invoice not found.'); END IF;
  BEGIN
    UPDATE booking SET end_date = p_new_end_date WHERE booking_id = p_booking_id;
  EXCEPTION WHEN exclusion_violation THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'OVERLAP', 'message', 'The room is already booked during the extension.');
  END;
  PERFORM recalculate_booking_bill(p_booking_id);
  SELECT total_room_charges, grand_total, payment_status
  INTO v_new_room, v_total, v_payment_status FROM billing_summary WHERE invoice_id = v_invoice;
  RETURN jsonb_build_object('success', true, 'message', 'Stay extended successfully.',
      'booking_id', p_booking_id, 'previous_check_out_date', v_old_end,
      'new_check_out_date', p_new_end_date, 'added_nights', p_new_end_date - v_old_end,
      'added_room_charge', v_new_room - v_old_room, 'grand_total', v_total,
      'payment_status', v_payment_status);
END;
$$;
