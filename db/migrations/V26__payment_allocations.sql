CREATE OR REPLACE FUNCTION record_invoice_payment(
  p_invoice_id UUID, p_amount NUMERIC, p_payment_method TEXT
) RETURNS JSONB LANGUAGE plpgsql AS $$
DECLARE v_booking BIGINT; v_status TEXT; v_total NUMERIC(10,2);
        v_paid NUMERIC(10,2); v_room NUMERIC(10,2); v_service NUMERIC(10,2);
        v_tax NUMERIC(10,2); v_room_left NUMERIC(10,2);
        v_service_left NUMERIC(10,2); v_tax_left NUMERIC(10,2);
        v_room_payment NUMERIC(10,2); v_service_payment NUMERIC(10,2);
        v_tax_payment NUMERIC(10,2); v_new_paid NUMERIC(10,2);
        v_payment_status TEXT; v_transaction UUID; v_date TIMESTAMP;
BEGIN
  SELECT booking_id INTO v_booking FROM billing_summary WHERE invoice_id = p_invoice_id;
  IF NOT FOUND THEN RETURN jsonb_build_object('success', false, 'error_code', 'NOT_FOUND', 'message', 'Invoice not found.'); END IF;
  SELECT booking_status INTO v_status FROM booking WHERE booking_id = v_booking FOR UPDATE;
  IF v_status <> 'CHECKED_IN' THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'INVALID_STATUS', 'message', 'Payments require a checked-in booking.');
  END IF;
  SELECT grand_total, amount_paid, total_room_charges, total_service_charges, total_tax_amount
  INTO v_total, v_paid, v_room, v_service, v_tax
  FROM billing_summary WHERE invoice_id = p_invoice_id FOR UPDATE;
  IF p_amount IS NULL OR p_amount <= 0 OR p_amount <> ROUND(p_amount, 2) THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'INVALID_AMOUNT', 'message', 'Enter a positive amount with at most two decimal places.');
  END IF;
  IF p_payment_method IS NULL OR p_payment_method NOT IN ('Cash', 'Card') THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'INVALID_METHOD', 'message', 'Choose Cash or Card.');
  END IF;
  IF p_amount > v_total - v_paid THEN
    RETURN jsonb_build_object('success', false, 'error_code', 'OVERPAYMENT', 'message', 'Payment amount exceeds the outstanding balance.');
  END IF;
  SELECT v_room - COALESCE(SUM(room_amount), 0),
         v_service - COALESCE(SUM(service_amount), 0),
         v_tax - COALESCE(SUM(tax_amount), 0)
  INTO v_room_left, v_service_left, v_tax_left
  FROM transactions WHERE invoice_id = p_invoice_id;
  IF p_amount = v_total - v_paid THEN
    v_room_payment := v_room_left;
    v_service_payment := v_service_left;
    v_tax_payment := v_tax_left;
  ELSE
    v_room_payment := LEAST(v_room_left, ROUND(p_amount * v_room_left / (v_total - v_paid), 2), p_amount);
    v_service_payment := LEAST(v_service_left, ROUND(p_amount * v_service_left / (v_total - v_paid), 2), p_amount - v_room_payment);
    v_tax_payment := p_amount - v_room_payment - v_service_payment;
  END IF;
  v_new_paid := v_paid + p_amount;
  v_payment_status := CASE WHEN v_new_paid = v_total THEN 'PAID' ELSE 'PARTIALLY_PAID' END;
  UPDATE billing_summary SET amount_paid = v_new_paid, payment_status = v_payment_status,
      payment_method = p_payment_method WHERE invoice_id = p_invoice_id;
  v_transaction := gen_random_uuid(); v_date := CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Colombo';
  INSERT INTO transactions (transaction_id, invoice_id, payment_date, amount,
      payment_method, room_amount, service_amount, tax_amount)
  VALUES (v_transaction, p_invoice_id, v_date, p_amount,
      p_payment_method, v_room_payment, v_service_payment, v_tax_payment);
  RETURN jsonb_build_object('success', true, 'transaction_id', v_transaction,
      'invoice_id', p_invoice_id, 'payment_date', v_date, 'amount', p_amount,
      'payment_method', p_payment_method, 'new_amount_paid', v_new_paid,
      'outstanding_balance', v_total - v_new_paid, 'payment_status', v_payment_status);
END;
$$;
