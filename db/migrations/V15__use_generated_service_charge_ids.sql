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

  -- PostgreSQL generates the service log ID.
  INSERT INTO service_charges (
    booking_id, service_id, service_dates, service_total
  )
  VALUES (
    p_booking_id, p_service_id, p_service_dates, v_service_total
  )
  RETURNING service_log_id INTO v_next_log_id;

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
