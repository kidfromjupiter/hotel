from datetime import date
from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class ReportsRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_occupancy_data(
        self, start_date: date, end_date: date, branch_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                WITH room_counts AS (
                  SELECT branch_id, COUNT(*) AS room_count
                  FROM room_details GROUP BY branch_id
                ), occupancy AS (
                  SELECT bk.branch_id,
                         SUM(GREATEST(0, LEAST(bk.end_date, %s::DATE) - GREATEST(bk.start_date, %s::DATE))) AS occupied_nights
                  FROM booking bk
                  WHERE bk.booking_status != 'CANCELLED'
                    AND bk.start_date < %s::DATE AND bk.end_date > %s::DATE
                  GROUP BY bk.branch_id
                )
                SELECT br.branch_name, COALESCE(rc.room_count, 0) AS total_rooms,
                       COALESCE(occ.occupied_nights, 0) AS occupied_nights,
                       COALESCE(rc.room_count, 0) * GREATEST(1, %s::DATE - %s::DATE) AS total_possible_nights,
                       ROUND(CASE WHEN COALESCE(rc.room_count, 0) > 0
                            THEN COALESCE(occ.occupied_nights, 0)::NUMERIC /
                                 (rc.room_count * GREATEST(1, %s::DATE - %s::DATE)) * 100
                            ELSE 0 END, 2) AS occupancy_rate_percent
                FROM branches br
                LEFT JOIN room_counts rc ON rc.branch_id = br.branch_id
                LEFT JOIN occupancy occ ON occ.branch_id = br.branch_id
                WHERE (%s::INT IS NULL OR br.branch_id = %s)
                ORDER BY br.branch_id
                """,
                (end_date, start_date, end_date, start_date, end_date, start_date,
                 end_date, start_date, branch_id, branch_id),
            )
            return list(cursor.fetchall())

    def get_guest_billing_data(
        self, payment_status: Optional[str] = None, branch_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT g.name AS guest_name, bk.booking_id,
                       COALESCE(bs.grand_total, 0) AS grand_total,
                       COALESCE(bs.amount_paid, 0) AS amount_paid,
                       GREATEST(0, COALESCE(bs.grand_total, 0) - COALESCE(bs.amount_paid, 0)) AS outstanding_balance,
                       COALESCE(bs.payment_status, 'UNPAID') AS payment_status,
                       (COALESCE(bs.payment_status, '') != 'PAID' AND bk.end_date < CURRENT_DATE) AS is_overdue
                FROM booking bk
                LEFT JOIN guests g ON g.guest_id = bk.guest_id
                LEFT JOIN billing_summary bs ON bs.booking_id = bk.booking_id
                WHERE bk.booking_status <> 'CANCELLED'
                  AND (%s::INT IS NULL OR bk.branch_id = %s)
                  AND (%s::TEXT IS NULL OR LOWER(COALESCE(bs.payment_status, 'UNPAID')) = LOWER(%s))
                ORDER BY bk.booking_id DESC
                """,
                (branch_id, branch_id, payment_status, payment_status),
            )
            return list(cursor.fetchall())

    def get_service_usage_data(
        self, branch_id: Optional[int] = None, service_id: Optional[int] = None,
        start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT br.branch_name, bk.room_number, cat.service_name,
                       COUNT(DISTINCT sc.booking_id) AS total_bookings_used,
                       SUM(sc.quantity) AS total_quantity,
                       SUM(COALESCE(sc.service_total, 0)) AS total_revenue
                FROM service_charges sc
                JOIN booking bk ON bk.booking_id = sc.booking_id
                JOIN branches br ON br.branch_id = bk.branch_id
                JOIN service_catalogue cat ON cat.service_id = sc.service_id
                WHERE (%s::INT IS NULL OR bk.branch_id = %s)
                  AND (%s::INT IS NULL OR sc.service_id = %s)
                  AND (%s::DATE IS NULL OR sc.usage_date >= %s::DATE)
                  AND (%s::DATE IS NULL OR sc.usage_date < %s::DATE)
                GROUP BY br.branch_id, br.branch_name, bk.room_number, sc.service_id, cat.service_name
                ORDER BY br.branch_id, bk.room_number, total_revenue DESC
                """,
                (branch_id, branch_id, service_id, service_id, start_date, start_date,
                 end_date, end_date),
            )
            return list(cursor.fetchall())

    def get_monthly_revenue_data(
        self, year: int, branch_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT br.branch_name, TRIM(TO_CHAR(t.payment_date, 'Month')) AS month,
                       SUM(t.room_amount) AS room_revenue,
                       SUM(t.service_amount) AS service_revenue,
                       SUM(t.tax_amount) AS tax_revenue,
                       SUM(t.amount) AS total_revenue
                FROM transactions t
                JOIN billing_summary bs ON bs.invoice_id = t.invoice_id
                JOIN booking bk ON bk.booking_id = bs.booking_id
                JOIN branches br ON br.branch_id = bk.branch_id
                WHERE t.payment_date >= MAKE_DATE(%s, 1, 1)
                  AND t.payment_date < MAKE_DATE(%s, 1, 1)
                  AND (%s::INT IS NULL OR bk.branch_id = %s)
                GROUP BY br.branch_id, br.branch_name, EXTRACT(MONTH FROM t.payment_date),
                         TO_CHAR(t.payment_date, 'Month')
                ORDER BY br.branch_id, EXTRACT(MONTH FROM t.payment_date)
                """,
                (year, year + 1, branch_id, branch_id),
            )
            return list(cursor.fetchall())

    def get_service_trends_data(
        self, limit: int = 5, start_date: Optional[date] = None,
        end_date: Optional[date] = None, branch_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if self.db is None:
            return []
        with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                WITH usage AS (
                  SELECT sc.service_id, SUM(sc.quantity) AS times_used,
                         COUNT(DISTINCT bk.guest_id) AS unique_guests,
                         SUM(COALESCE(sc.service_total, 0)) AS total_revenue
                  FROM service_charges sc
                  JOIN booking bk ON bk.booking_id = sc.booking_id
                  WHERE (%s::INT IS NULL OR bk.branch_id = %s)
                    AND (%s::DATE IS NULL OR sc.usage_date >= %s::DATE)
                    AND (%s::DATE IS NULL OR sc.usage_date < %s::DATE)
                  GROUP BY sc.service_id
                  ORDER BY times_used DESC, sc.service_id
                  LIMIT %s
                )
                SELECT ROW_NUMBER() OVER (ORDER BY usage.times_used DESC, usage.service_id) AS rank,
                       cat.service_name, usage.times_used, usage.unique_guests, usage.total_revenue
                FROM usage JOIN service_catalogue cat ON cat.service_id = usage.service_id
                ORDER BY rank
                """,
                (branch_id, branch_id, start_date, start_date, end_date, end_date, limit),
            )
            return list(cursor.fetchall())
