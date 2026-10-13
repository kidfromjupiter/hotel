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
