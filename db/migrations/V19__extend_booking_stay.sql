-- Extend a checked-in stay while preserving room availability and billing consistency.
CREATE OR REPLACE FUNCTION extend_booking_stay(
  p_booking_id BIGINT,
  p_new_end_date DATE
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  v_start_date DATE;
  v_previous_end_date DATE;
  v_status VARCHAR(50);
  v_room_number SMALLINT;
  v_branch_id INT;
  v_daily_rate NUMERIC(10,2);
  v_room_discount NUMERIC(10,2) := 0.0;
  v_old_nights INT;
  v_added_nights INT;
  v_effective_nightly_rate NUMERIC(12,2);
  v_added_room_charge NUMERIC(12,2);
  v_invoice_id UUID;
  v_room_charges NUMERIC(12,2);
  v_service_charges NUMERIC(12,2);
  v_tax_amount NUMERIC(12,2);
  v_amount_paid NUMERIC(12,2);
  v_grand_total NUMERIC(12,2);
  v_payment_status VARCHAR(50);
BEGIN
  SELECT
    b.start_date,
    b.end_date,
    b.booking_status,
    b.room_number,
    b.branch_id,
    rt.daily_rate,
    COALESCE(m.room_discount_percentage, 0.0)
  INTO
    v_start_date,
    v_previous_end_date,
    v_status,
    v_room_number,
    v_branch_id,
    v_daily_rate,
    v_room_discount
  FROM booking b
  JOIN room_details rd
    ON rd.room_number = b.room_number AND rd.branch_id = b.branch_id
  JOIN room_types rt ON rt.room_type_id = rd.room_type_id
  LEFT JOIN guests g ON g.guest_id = b.guest_id
  LEFT JOIN skynest_membership m ON m.membership_id = g.membership_id
  WHERE b.booking_id = p_booking_id
  FOR UPDATE OF b;

  IF NOT FOUND THEN
    RETURN jsonb_build_object(
      'success', false,
      'error_code', 'NOT_FOUND',
      'message', 'Booking not found.'
    );
  END IF;

  IF v_status <> 'CHECKED_IN' THEN
    RETURN jsonb_build_object(
      'success', false,
      'error_code', 'INVALID_STATUS',
      'message', 'Only checked-in bookings can be extended.'
    );
  END IF;

  IF p_new_end_date <= v_previous_end_date THEN
    RETURN jsonb_build_object(
      'success', false,
      'error_code', 'INVALID_DATE',
      'message', 'The new check-out date must be later than the current check-out date.'
    );
  END IF;

  IF EXISTS (
    SELECT 1
    FROM booking other_booking
    WHERE other_booking.room_number = v_room_number
      AND other_booking.branch_id = v_branch_id
      AND other_booking.booking_id <> p_booking_id
      AND other_booking.booking_status IN ('CONFIRMED', 'CHECKED_IN')
      AND other_booking.start_date < p_new_end_date
      AND other_booking.end_date > v_previous_end_date
  ) THEN
    RETURN jsonb_build_object(
      'success', false,
      'error_code', 'OVERLAP',
      'message', 'The room is already booked during the requested extension period.'
    );
  END IF;

  SELECT
    bs.invoice_id,
    COALESCE(bs.total_room_charges, 0.0),
    COALESCE(bs.total_service_charges, 0.0),
    COALESCE(bs.total_tax_amount, 0.0),
    COALESCE(bs.amount_paid, 0.0)
  INTO
    v_invoice_id,
    v_room_charges,
    v_service_charges,
    v_tax_amount,
    v_amount_paid
  FROM billing_summary bs
  WHERE bs.booking_id = p_booking_id
  FOR UPDATE;

  IF NOT FOUND THEN
    RETURN jsonb_build_object(
      'success', false,
      'error_code', 'BILLING_NOT_FOUND',
      'message', 'The booking invoice could not be found.'
    );
  END IF;

  v_old_nights := GREATEST(1, v_previous_end_date - v_start_date);
  v_added_nights := p_new_end_date - v_previous_end_date;

  IF v_room_charges > 0 THEN
    v_effective_nightly_rate := ROUND(v_room_charges / v_old_nights, 2);
  ELSE
    v_effective_nightly_rate := ROUND(
      COALESCE(v_daily_rate, 0.0) * (1.0 - (v_room_discount / 100.0)),
      2
    );
  END IF;

  v_added_room_charge := ROUND(v_effective_nightly_rate * v_added_nights, 2);
  v_room_charges := v_room_charges + v_added_room_charge;
  v_grand_total := v_room_charges + v_service_charges + v_tax_amount;
  v_payment_status := CASE
    WHEN v_grand_total > 0 AND v_amount_paid >= v_grand_total THEN 'PAID'
    WHEN v_amount_paid > 0 THEN 'PARTIALLY_PAID'
    ELSE 'UNPAID'
  END;

  UPDATE booking
  SET end_date = p_new_end_date
  WHERE booking_id = p_booking_id;

  UPDATE billing_summary
  SET total_room_charges = v_room_charges,
      grand_total = v_grand_total,
      payment_status = v_payment_status
  WHERE invoice_id = v_invoice_id;

  RETURN jsonb_build_object(
    'success', true,
    'message', 'Stay extended successfully.',
    'booking_id', p_booking_id,
    'previous_check_out_date', v_previous_end_date,
    'new_check_out_date', p_new_end_date,
    'added_nights', v_added_nights,
    'added_room_charge', v_added_room_charge,
    'grand_total', v_grand_total,
    'payment_status', v_payment_status
  );
END;
$$;
