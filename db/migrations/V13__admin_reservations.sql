CREATE OR REPLACE FUNCTION get_admin_reservations(
  p_branch_id INT DEFAULT NULL,
  p_status TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  result JSONB;
BEGIN
  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'booking_id', bk.booking_id,
        'booking_ref', bk.booking_ref,
        'guest_id', bk.guest_id,
        'guest_name', COALESCE(g.name, 'Unknown Guest'),
        'guest_contact', g.phone_number::TEXT,
        'room_number', bk.room_number,
        'room_type_id', rd.room_type_id,
        'branch_id', bk.branch_id,
        'branch_name', INITCAP(COALESCE(b.branch_name, 'Unknown')),
        'booking_status', bk.booking_status,
        'start_date', bk.start_date,
        'end_date', bk.end_date,
        'nights', (bk.end_date - bk.start_date),
        'adult_count', bk.adult_count,
        'children_count', bk.children_count,
        'total_room_charges', COALESCE(bs.total_room_charges, 0.0),
        'total_service_charges', COALESCE(bs.total_service_charges, 0.0),
        'total_tax_amount', COALESCE(bs.total_tax_amount, 0.0),
        'grand_total', COALESCE(bs.grand_total, 0.0),
        'amount_paid', COALESCE(bs.amount_paid, 0.0),
        'balance_amount', GREATEST((COALESCE(bs.grand_total, 0.0) - COALESCE(bs.amount_paid, 0.0)), 0.0),
        'invoice_status', COALESCE(bs.payment_status, 'UNPAID'),
        'payment_method', COALESCE(bs.payment_method, 'NONE')
      )
      ORDER BY bk.booking_id DESC
    ),
    '[]'::JSONB
  )
  INTO result
  FROM booking bk
  LEFT JOIN guests g ON bk.guest_id = g.guest_id
  LEFT JOIN branches b ON bk.branch_id = b.branch_id
  LEFT JOIN room_details rd ON bk.room_number = rd.room_number AND bk.branch_id = rd.branch_id
  LEFT JOIN billing_summary bs ON bk.booking_id = bs.booking_id
  WHERE (p_branch_id IS NULL OR bk.branch_id = p_branch_id)
    AND (p_status IS NULL OR p_status = '' OR bk.booking_status ILIKE p_status);
    
  RETURN result;
END;
$$;
