-- V8: Database functions for hotel management reports

-- 1. Occupancy report per branch over date range
CREATE OR REPLACE FUNCTION get_occupancy_report(
  p_start_date DATE,
  p_end_date DATE,
  p_branch_id INT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
  v_period_days INT;
  result JSONB;
BEGIN
  v_period_days := GREATEST(1, (p_end_date - p_start_date));

  SELECT COALESCE(
    jsonb_agg(
      jsonb_build_object(
        'branch_name', INITCAP(b.branch_name),
        'total_rooms', COALESCE(rc.room_count, 0),
        'occupied_nights', COALESCE(occ.occupied_nights, 0),
        'total_possible_nights', (COALESCE(rc.room_count, 0) * v_period_days),
        'occupancy_rate_percent', ROUND(
          CASE 
            WHEN (COALESCE(rc.room_count, 0) * v_period_days) > 0 
            THEN (COALESCE(occ.occupied_nights, 0)::NUMERIC / (rc.room_count * v_period_days)::NUMERIC) * 100.0
            ELSE 0.0 
          END, 2
        )
      )
      ORDER BY b.branch_id
    ),
    '[]'::JSONB
  )
  INTO result
  FROM branches b
  LEFT JOIN (
    SELECT branch_id, COUNT(*) AS room_count
    FROM room_details
    GROUP BY branch_id
  ) rc ON b.branch_id = rc.branch_id
  LEFT JOIN (
    SELECT 
      bk.branch_id,
      SUM(
        GREATEST(0, LEAST(bk.end_date, p_end_date) - GREATEST(bk.start_date, p_start_date))
      ) AS occupied_nights
    FROM booking bk
    WHERE bk.booking_status != 'CANCELLED'
      AND bk.start_date < p_end_date
      AND bk.end_date > p_start_date
    GROUP BY bk.branch_id
  ) occ ON b.branch_id = occ.branch_id
  WHERE (p_branch_id IS NULL OR b.branch_id = p_branch_id);

  RETURN result;
END;
$$;


-- 2. Guest billing summaries with balances and overdue status
CREATE OR REPLACE FUNCTION get_guest_billing_report(
  p_payment_status TEXT DEFAULT NULL,
  p_branch_id INT DEFAULT NULL
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
        'guest_name', COALESCE(g.name, 'Guest'),
        'booking_id', bk.booking_id,
        'grand_total', COALESCE(bs.grand_total, 0.0),
        'amount_paid', COALESCE(bs.amount_paid, 0.0),
        'outstanding_balance', GREATEST(0.0, COALESCE(bs.grand_total, 0.0) - COALESCE(bs.amount_paid, 0.0)),
        'payment_status', COALESCE(bs.payment_status, 'UNPAID'),
        'is_overdue', (COALESCE(bs.payment_status, '') != 'PAID' AND bk.end_date < CURRENT_DATE)
      )
      ORDER BY bk.booking_id DESC
    ),
    '[]'::JSONB
  )
  INTO result
  FROM booking bk
  LEFT JOIN guests g ON bk.guest_id = g.guest_id
  LEFT JOIN billing_summary bs ON bk.booking_id = bs.booking_id
  WHERE (p_branch_id IS NULL OR bk.branch_id = p_branch_id)
    AND (p_payment_status IS NULL OR LOWER(bs.payment_status) = LOWER(p_payment_status));

  RETURN result;
END;
$$;


-- 3. Service usage counts and revenue aggregation
CREATE OR REPLACE FUNCTION get_service_usage_report(
  p_branch_id INT DEFAULT NULL,
  p_service_id INT DEFAULT NULL,
  p_start_date DATE DEFAULT NULL,
  p_end_date DATE DEFAULT NULL
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
        'service_name', sc_cat.service_name,
        'total_bookings_used', su.total_bookings_used,
        'total_days_used', su.total_days_used,
        'total_revenue', su.total_revenue
      )
      ORDER BY su.total_revenue DESC
    ),
    '[]'::JSONB
  )
  INTO result
  FROM (
    SELECT 
      sc.service_id,
      COUNT(DISTINCT sc.booking_id) AS total_bookings_used,
      SUM(COALESCE(sc.service_dates, 1)) AS total_days_used,
      SUM(COALESCE(sc.service_total, 0.0)) AS total_revenue
    FROM service_charges sc
    JOIN booking bk ON sc.booking_id = bk.booking_id
    WHERE (p_branch_id IS NULL OR bk.branch_id = p_branch_id)
      AND (p_service_id IS NULL OR sc.service_id = p_service_id)
      AND (p_start_date IS NULL OR bk.start_date >= p_start_date)
      AND (p_end_date IS NULL OR bk.end_date <= p_end_date)
    GROUP BY sc.service_id
  ) su
  JOIN service_catalogue sc_cat ON su.service_id = sc_cat.service_id;

  RETURN result;
END;
$$;


-- 4. Monthly revenue breakdown
CREATE OR REPLACE FUNCTION get_monthly_revenue_report(
  p_year INT,
  p_branch_id INT DEFAULT NULL
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
        'branch_name', INITCAP(b.branch_name),
        'month', TRIM(TO_CHAR(bk.start_date, 'Month')),
        'room_revenue', COALESCE(SUM(bs.total_room_charges), 0.0),
        'service_revenue', COALESCE(SUM(bs.total_service_charges), 0.0),
        'total_revenue', COALESCE(SUM(bs.grand_total), 0.0)
      )
      ORDER BY b.branch_id, EXTRACT(MONTH FROM bk.start_date)
    ),
    '[]'::JSONB
  )
  INTO result
  FROM booking bk
  JOIN branches b ON bk.branch_id = b.branch_id
  LEFT JOIN billing_summary bs ON bk.booking_id = bs.booking_id
  WHERE EXTRACT(YEAR FROM bk.start_date) = p_year
    AND (p_branch_id IS NULL OR bk.branch_id = p_branch_id)
  GROUP BY b.branch_id, b.branch_name, EXTRACT(MONTH FROM bk.start_date), TO_CHAR(bk.start_date, 'Month');

  RETURN result;
END;
$$;


-- 5. Service trends and ranking
CREATE OR REPLACE FUNCTION get_service_trends_report(
  p_limit INT DEFAULT 5,
  p_start_date DATE DEFAULT NULL,
  p_end_date DATE DEFAULT NULL
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
        'rank', row_number() over (order by st.times_used desc),
        'service_name', sc_cat.service_name,
        'times_used', st.times_used,
        'total_revenue', st.total_revenue
      )
    ),
    '[]'::JSONB
  )
  INTO result
  FROM (
    SELECT 
      sc.service_id,
      COUNT(sc.service_log_id) AS times_used,
      SUM(COALESCE(sc.service_total, 0.0)) AS total_revenue
    FROM service_charges sc
    JOIN booking bk ON sc.booking_id = bk.booking_id
    WHERE (p_start_date IS NULL OR bk.start_date >= p_start_date)
      AND (p_end_date IS NULL OR bk.end_date <= p_end_date)
    GROUP BY sc.service_id
    ORDER BY times_used DESC
    LIMIT p_limit
  ) st
  JOIN service_catalogue sc_cat ON st.service_id = sc_cat.service_id;

  RETURN result;
END;
$$;
