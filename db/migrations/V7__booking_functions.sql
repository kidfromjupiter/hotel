-- Booking creation keeps its booking and billing writes in one database function.
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
    booking_ref,
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
    'SKN-' || p_booking_id,
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

  RETURN jsonb_build_object('booking_id', p_booking_id, 'booking_ref', 'SKN-' || p_booking_id::TEXT);
END;
$$;
