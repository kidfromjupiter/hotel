from datetime import date
from typing import Any, Dict, List, Optional

from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor


class ReportsRepo:
    def __init__(self, db: Optional[connection] = None) -> None:
        self.db = db

    def get_occupancy_data(
        self,
        start_date: date,
        end_date: date,
        branch_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT get_occupancy_report(%s, %s, %s)",
                    (start_date, end_date, branch_id),
                )
                row = cursor.fetchone()
                if row and "get_occupancy_report" in row and row["get_occupancy_report"]:
                    return row["get_occupancy_report"]
        return []

    def get_guest_billing_data(
        self,
        payment_status: Optional[str] = None,
        branch_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT get_guest_billing_report(%s, %s)",
                    (payment_status, branch_id),
                )
                row = cursor.fetchone()
                if row and "get_guest_billing_report" in row and row["get_guest_billing_report"] is not None:
                    return row["get_guest_billing_report"]
        return []

    def get_service_usage_data(
        self,
        branch_id: Optional[int] = None,
        service_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT get_service_usage_report(%s, %s, %s, %s)",
                    (branch_id, service_id, start_date, end_date),
                )
                row = cursor.fetchone()
                if row and "get_service_usage_report" in row and row["get_service_usage_report"] is not None:
                    return row["get_service_usage_report"]
        return []

    def get_monthly_revenue_data(
        self,
        year: int,
        branch_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT get_monthly_revenue_report(%s, %s)",
                    (year, branch_id),
                )
                row = cursor.fetchone()
                if row and "get_monthly_revenue_report" in row and row["get_monthly_revenue_report"] is not None:
                    return row["get_monthly_revenue_report"]
        return []

    def get_service_trends_data(
        self,
        limit: int = 5,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        if self.db is not None:
            with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT get_service_trends_report(%s, %s, %s)",
                    (limit, start_date, end_date),
                )
                row = cursor.fetchone()
                if row and "get_service_trends_report" in row and row["get_service_trends_report"] is not None:
                    return row["get_service_trends_report"]
        return []
