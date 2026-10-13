-- V20: Database-backed guest payment history lookup for staff.

CREATE OR REPLACE FUNCTION get_guest_payment_history(
  p_query TEXT,
  p_branch_id INT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  v_query TEXT := BTRIM(COALESCE(p_query, ''));
  v_digits TEXT;
  v_guest_id INT;
  v_guest JSONB;
  v_summary JSONB;
  v_bookings JSONB;
BEGIN
  IF v_query = '' THEN
    RETURN NULL;
  END IF;

  -- An exact guest ID wins. If it does not exist, interpret the value as a
  -- phone number and compare its normalized local digits.
  SELECT g.guest_id
  INTO v_guest_id
  FROM guests g
  WHERE g.guest_id::TEXT = v_query
  LIMIT 1;

  IF v_guest_id IS NULL THEN
    v_digits := REGEXP_REPLACE(v_query, '[^0-9]', '', 'g');
    IF v_digits LIKE '94%' THEN
      v_digits := SUBSTRING(v_digits FROM 3);
    ELSIF v_digits LIKE '0%' THEN
      v_digits := SUBSTRING(v_digits FROM 2);
    END IF;

    SELECT g.guest_id
    INTO v_guest_id
    FROM guests g
    WHERE g.phone_number::TEXT = v_digits
    LIMIT 1;
  END IF;

  IF v_guest_id IS NULL THEN
    RETURN NULL;
  END IF;

  SELECT jsonb_build_object(
    'guest_id', g.guest_id,
    'name', g.name,
    'phone_number', g.phone_number::TEXT
  )
  INTO v_guest
  FROM guests g
  WHERE g.guest_id = v_guest_id;

  SELECT jsonb_build_object(
    'booking_count', COUNT(bk.booking_id),
    'grand_total', COALESCE(SUM(COALESCE(bs.grand_total, 0.0)), 0.0),
    'amount_paid', COALESCE(SUM(COALESCE(bs.amount_paid, 0.0)), 0.0),
    'outstanding_balance', COALESCE(
      SUM(GREATEST(0.0, COALESCE(bs.grand_total, 0.0) - COALESCE(bs.amount_paid, 0.0))),
      0.0
    )
  )
  INTO v_summary
  FROM booking bk
  LEFT JOIN billing_summary bs ON bs.booking_id = bk.booking_id
  WHERE bk.guest_id = v_guest_id
    AND (p_branch_id IS NULL OR bk.branch_id = p_branch_id);

  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'booking_id', bk.booking_id,
        'booking_ref', bk.booking_ref,
        'branch_id', bk.branch_id,
        'branch_name', INITCAP(COALESCE(br.branch_name, 'Unknown')),
        'start_date', bk.start_date,
        'end_date', bk.end_date,
        'booking_status', bk.booking_status,
        'invoice_id', bs.invoice_id,
        'payment_method', COALESCE(bs.payment_method, 'NONE'),
        'payment_status', COALESCE(bs.payment_status, 'UNPAID'),
        'grand_total', COALESCE(bs.grand_total, 0.0),
        'amount_paid', COALESCE(bs.amount_paid, 0.0),
        'outstanding_balance', GREATEST(
          0.0,
          COALESCE(bs.grand_total, 0.0) - COALESCE(bs.amount_paid, 0.0)
        )
      )
      ORDER BY bk.start_date DESC, bk.booking_id DESC
    ),
    '[]'::JSONB
  )
  INTO v_bookings
  FROM booking bk
  LEFT JOIN branches br ON br.branch_id = bk.branch_id
  LEFT JOIN billing_summary bs ON bs.booking_id = bk.booking_id
  WHERE bk.guest_id = v_guest_id
    AND (p_branch_id IS NULL OR bk.branch_id = p_branch_id);

  RETURN jsonb_build_object(
    'guest', v_guest,
    'summary', v_summary,
    'bookings', v_bookings
  );
END;
$$;
