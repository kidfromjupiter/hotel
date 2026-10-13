-- Expose the real invoice and its charge breakdown to the billing screen.
CREATE OR REPLACE FUNCTION get_booking_by_id(p_booking_id BIGINT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT jsonb_build_object(
    'booking_id', bk.booking_id,
    'booking_ref', bk.booking_ref,
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
    'invoice_id', bs.invoice_id,
    'total_room_charges', COALESCE(bs.total_room_charges, 0.0),
    'total_service_charges', COALESCE(bs.total_service_charges, 0.0),
    'total_tax_amount', COALESCE(bs.total_tax_amount, 0.0),
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

-- Lock booking first, then invoice, consistently with stay extension and checkout.
CREATE FUNCTION record_invoice_payment(
  p_invoice_id UUID,
  p_amount NUMERIC,
  p_payment_method TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  v_booking_id BIGINT;
  v_booking_status VARCHAR(50);
  v_grand_total NUMERIC(10,2);
  v_amount_paid NUMERIC(10,2);
  v_new_amount_paid NUMERIC(10,2);
  v_payment_status VARCHAR(50);
  v_transaction_id UUID;
  v_payment_date TIMESTAMP;
BEGIN
  SELECT booking_id INTO v_booking_id
  FROM billing_summary WHERE invoice_id = p_invoice_id;

  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'NOT_FOUND', 'message', 'Invoice not found.');
  END IF;

  SELECT booking_status INTO v_booking_status
  FROM booking WHERE booking_id = v_booking_id FOR UPDATE;

  IF v_booking_status <> 'CHECKED_IN' THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'INVALID_STATUS', 'message', 'Payments require a checked-in booking.');
  END IF;

  SELECT grand_total, COALESCE(amount_paid, 0.0)
  INTO v_grand_total, v_amount_paid
  FROM billing_summary WHERE invoice_id = p_invoice_id FOR UPDATE;

  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'NOT_FOUND', 'message', 'Invoice not found.');
  END IF;

  IF p_amount IS NULL OR p_amount <= 0 OR p_amount <> ROUND(p_amount, 2) THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'INVALID_AMOUNT', 'message', 'Enter a positive amount with at most two decimal places.');
  END IF;

  IF p_payment_method NOT IN ('Cash', 'Card') OR p_payment_method IS NULL THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'INVALID_METHOD', 'message', 'Choose Cash or Card.');
  END IF;

  IF p_amount > v_grand_total - v_amount_paid THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'OVERPAYMENT', 'message', 'Payment amount exceeds the outstanding balance.');
  END IF;

  v_new_amount_paid := v_amount_paid + p_amount;
  v_payment_status := CASE WHEN v_new_amount_paid >= v_grand_total THEN 'PAID' ELSE 'PARTIALLY_PAID' END;

  UPDATE billing_summary
  SET amount_paid = v_new_amount_paid,
      payment_status = v_payment_status,
      payment_method = p_payment_method
  WHERE invoice_id = p_invoice_id;

  v_transaction_id := gen_random_uuid();
  v_payment_date := CURRENT_TIMESTAMP;
  INSERT INTO transactions (transaction_id, invoice_id, payment_date, amount, payment_method)
  VALUES (v_transaction_id, p_invoice_id, v_payment_date, p_amount, p_payment_method);

  RETURN jsonb_build_object(
    'success', true,
    'transaction_id', v_transaction_id,
    'invoice_id', p_invoice_id,
    'payment_date', v_payment_date,
    'amount', p_amount,
    'payment_method', p_payment_method,
    'new_amount_paid', v_new_amount_paid,
    'outstanding_balance', v_grand_total - v_new_amount_paid,
    'payment_status', v_payment_status
  );
END;
$$;

-- Keep the existing two-argument signature for existing clients; its method is
-- accepted for compatibility but checkout itself never records a payment.
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
  v_booking_status VARCHAR(50);
  v_invoice_id UUID;
  v_grand_total NUMERIC(10,2);
  v_amount_paid NUMERIC(10,2);
BEGIN
  SELECT room_number, branch_id, booking_status
  INTO v_room_num, v_branch_id, v_booking_status
  FROM booking WHERE booking_id = p_booking_id FOR UPDATE;

  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'NOT_FOUND', 'message', 'Booking not found.');
  END IF;

  IF v_booking_status <> 'CHECKED_IN' THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'INVALID_STATUS', 'message', 'Only checked-in bookings can be checked out.');
  END IF;

  SELECT invoice_id, grand_total, COALESCE(amount_paid, 0.0)
  INTO v_invoice_id, v_grand_total, v_amount_paid
  FROM billing_summary WHERE booking_id = p_booking_id FOR UPDATE;

  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'BILLING_NOT_FOUND', 'message', 'The booking invoice could not be found.');
  END IF;

  IF v_amount_paid < v_grand_total THEN
    RETURN jsonb_build_object(
      'success', false,
      'error_code', 'OUTSTANDING_BALANCE',
      'message', 'Outstanding unpaid balance exists; checkout requires full payment.',
      'outstanding_balance', v_grand_total - v_amount_paid
    );
  END IF;

  UPDATE booking SET booking_status = 'CHECKED_OUT', checked_out_time = CURRENT_TIME
  WHERE booking_id = p_booking_id;

  UPDATE room_details SET room_status = 'AVAILABLE'
  WHERE room_number = v_room_num AND branch_id = v_branch_id;

  RETURN jsonb_build_object(
    'success', true,
    'message', 'Booking checked out successfully',
    'booking_id', p_booking_id,
    'invoice_id', v_invoice_id,
    'payment_status', 'PAID',
    'grand_total', v_grand_total,
    'amount_paid', v_amount_paid
  );
END;
$$;
