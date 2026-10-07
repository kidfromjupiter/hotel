-- V12: Fix database functions for hotel management reports (Grouping Errors)

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
        'branch_name', INITCAP(mrb.branch_name),
        'month', TRIM(mrb.month_name),
        'room_revenue', mrb.room_revenue,
        'service_revenue', mrb.service_revenue,
        'total_revenue', mrb.total_revenue
      )
      ORDER BY mrb.branch_id, mrb.month_num
    ),
    '[]'::JSONB
  )
  INTO result
  FROM (
    SELECT 
      b.branch_id,
      b.branch_name,
      EXTRACT(MONTH FROM bk.start_date) AS month_num,
      TO_CHAR(bk.start_date, 'Month') AS month_name,
      COALESCE(SUM(bs.total_room_charges), 0.0) AS room_revenue,
      COALESCE(SUM(bs.total_service_charges), 0.0) AS service_revenue,
      COALESCE(SUM(bs.grand_total), 0.0) AS total_revenue
    FROM booking bk
    JOIN branches b ON bk.branch_id = b.branch_id
    LEFT JOIN billing_summary bs ON bk.booking_id = bs.booking_id
    WHERE EXTRACT(YEAR FROM bk.start_date) = p_year
      AND (p_branch_id IS NULL OR bk.branch_id = p_branch_id)
    GROUP BY b.branch_id, b.branch_name, EXTRACT(MONTH FROM bk.start_date), TO_CHAR(bk.start_date, 'Month')
  ) mrb;

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
        'rank', str.rank,
        'service_name', sc_cat.service_name,
        'times_used', str.times_used,
        'total_revenue', str.total_revenue
      )
    ),
    '[]'::JSONB
  )
  INTO result
  FROM (
    SELECT 
      st.service_id,
      st.times_used,
      st.total_revenue,
      row_number() OVER (ORDER BY st.times_used DESC) as rank
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
  ) str
  JOIN service_catalogue sc_cat ON str.service_id = sc_cat.service_id;

  RETURN result;
END;
$$;
