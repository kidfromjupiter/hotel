from datetime import date
from typing import List, Optional, Dict, Any

from app.schemas.reports import (
    PeriodSchema,
    BranchOccupancyItem,
    OccupancyReportResponse,
    GuestBillingItem,
    GuestBillingReportResponse,
    ServiceUsageItem,
    ServiceUsageReportResponse,
    MonthlyRevenueItem,
    MonthlyRevenueReportResponse,
    ServiceTrendItem,
    ServiceTrendsReportResponse,
)

# Sample reference data for branches and services
BRANCH_DATA = [
    {"branch_id": 1, "branch_name": "Colombo", "total_rooms": 20},
    {"branch_id": 2, "branch_name": "Kandy", "total_rooms": 15},
    {"branch_id": 3, "branch_name": "Galle", "total_rooms": 15},
]

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


class ReportService:
    """Business logic for generating SkyNest management reports."""

    def get_occupancy_report(
        self,
        start_date: date,
        end_date: date,
        branch_id: Optional[int] = None,
    ) -> OccupancyReportResponse:
        period_days = max(1, (end_date - start_date).days)
        branches = BRANCH_DATA if branch_id is None else [b for b in BRANCH_DATA if b["branch_id"] == branch_id]

        items: List[BranchOccupancyItem] = []
        for b in branches:
            total_rooms = b["total_rooms"]
            total_possible_nights = total_rooms * period_days
            # Simulated occupied nights or calculated from active bookings
            occupied_nights = min(int(total_possible_nights * 0.45), total_possible_nights)
            rate = round((occupied_nights / total_possible_nights) * 100, 2) if total_possible_nights > 0 else 0.0

            items.append(
                BranchOccupancyItem(
                    branch_name=b["branch_name"],
                    total_rooms=total_rooms,
                    occupied_nights=occupied_nights,
                    total_possible_nights=total_possible_nights,
                    occupancy_rate_percent=rate,
                )
            )

        return OccupancyReportResponse(
            period=PeriodSchema(start_date=start_date, end_date=end_date),
            branches=items,
        )

    def get_guest_billing_report(
        self,
        payment_status: Optional[str] = None,
        branch_id: Optional[int] = None,
    ) -> GuestBillingReportResponse:
        # Default sample dataset representing billing summaries
        sample_billings = [
            {
                "guest_name": "Amal Perera",
                "booking_id": 500001,
                "grand_total": 75750.00,
                "amount_paid": 30000.00,
                "payment_status": "PARTIAL",
                "end_date": date(2026, 1, 15),
                "branch_id": 1,
            },
            {
                "guest_name": "Nimal Silva",
                "booking_id": 500002,
                "grand_total": 120000.00,
                "amount_paid": 120000.00,
                "payment_status": "PAID",
                "end_date": date(2026, 2, 10),
                "branch_id": 1,
            },
            {
                "guest_name": "Kasun Fernando",
                "booking_id": 500003,
                "grand_total": 45000.00,
                "amount_paid": 0.00,
                "payment_status": "UNPAID",
                "end_date": date(2026, 1, 5),
                "branch_id": 2,
            },
            {
                "guest_name": "Sarah Jenkins",
                "booking_id": 500004,
                "grand_total": 95000.00,
                "amount_paid": 50000.00,
                "payment_status": "PARTIAL",
                "end_date": date(2026, 10, 20),
                "branch_id": 3,
            },
        ]

        today = date.today()
        items: List[GuestBillingItem] = []

        for b in sample_billings:
            if branch_id is not None and b["branch_id"] != branch_id:
                continue
            if payment_status is not None and b["payment_status"].upper() != payment_status.upper():
                continue

            outstanding = max(0.0, float(b["grand_total"] - b["amount_paid"]))
            is_overdue = b["payment_status"] != "PAID" and b["end_date"] < today

            items.append(
                GuestBillingItem(
                    guest_name=b["guest_name"],
                    booking_id=b["booking_id"],
                    grand_total=float(b["grand_total"]),
                    amount_paid=float(b["amount_paid"]),
                    outstanding_balance=outstanding,
                    payment_status=b["payment_status"],
                    is_overdue=is_overdue,
                )
            )

        return GuestBillingReportResponse(data=items)

    def get_service_usage_report(
        self,
        branch_id: Optional[int] = None,
        service_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> ServiceUsageReportResponse:
        sample_services = [
            {"service_id": 1, "service_name": "Spa Package", "total_bookings_used": 42, "total_days_used": 89, "total_revenue": 504000.0, "branch_id": 1},
            {"service_id": 2, "service_name": "Airport Pickup", "total_bookings_used": 35, "total_days_used": 35, "total_revenue": 175000.0, "branch_id": 1},
            {"service_id": 3, "service_name": "Tea Tour", "total_bookings_used": 28, "total_days_used": 28, "total_revenue": 238000.0, "branch_id": 2},
            {"service_id": 4, "service_name": "Whale Watching", "total_bookings_used": 19, "total_days_used": 19, "total_revenue": 304000.0, "branch_id": 3},
        ]

        items: List[ServiceUsageItem] = []
        for s in sample_services:
            if branch_id is not None and s["branch_id"] != branch_id:
                continue
            if service_id is not None and s["service_id"] != service_id:
                continue

            items.append(
                ServiceUsageItem(
                    service_name=s["service_name"],
                    total_bookings_used=s["total_bookings_used"],
                    total_days_used=s["total_days_used"],
                    total_revenue=float(s["total_revenue"]),
                )
            )

        return ServiceUsageReportResponse(data=items)

    def get_monthly_revenue_report(
        self,
        year: int,
        branch_id: Optional[int] = None,
    ) -> MonthlyRevenueReportResponse:
        branches = BRANCH_DATA if branch_id is None else [b for b in BRANCH_DATA if b["branch_id"] == branch_id]

        items: List[MonthlyRevenueItem] = []
        # Return summary for active months of the year
        months_to_report = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October"]

        for b in branches:
            for m in months_to_report:
                room_rev = 450000.00
                service_rev = 120000.00
                items.append(
                    MonthlyRevenueItem(
                        branch_name=b["branch_name"],
                        month=m,
                        room_revenue=room_rev,
                        service_revenue=service_rev,
                        total_revenue=room_rev + service_rev,
                    )
                )

        return MonthlyRevenueReportResponse(year=year, data=items)

    def get_service_trends_report(
        self,
        limit: int = 5,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> ServiceTrendsReportResponse:
        all_trends = [
            {"service_name": "Room Service", "times_used": 312, "total_revenue": 780000.00},
            {"service_name": "Spa Treatment", "times_used": 189, "total_revenue": 756000.00},
            {"service_name": "Airport Pickup", "times_used": 145, "total_revenue": 725000.00},
            {"service_name": "Tea Plantation Tour", "times_used": 98, "total_revenue": 833000.00},
            {"service_name": "Whale Watching Cruise", "times_used": 76, "total_revenue": 1216000.00},
            {"service_name": "Laundry Service", "times_used": 62, "total_revenue": 186000.00},
        ]

        # Sort descending by times_used
        sorted_trends = sorted(all_trends, key=lambda x: x["times_used"], reverse=True)[:limit]

        items = [
            ServiceTrendItem(
                rank=idx + 1,
                service_name=s["service_name"],
                times_used=s["times_used"],
                total_revenue=s["total_revenue"],
            )
            for idx, s in enumerate(sorted_trends)
        ]

        period = PeriodSchema(start_date=start_date, end_date=end_date) if (start_date and end_date) else None
        return ServiceTrendsReportResponse(period=period, top_services=items)


report_service = ReportService()
