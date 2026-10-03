from datetime import date
from typing import List, Optional

from app.repositories.reports_repo import ReportsRepo
from app.schemas.reports import (
    BranchOccupancyItem,
    GuestBillingItem,
    GuestBillingReportResponse,
    MonthlyRevenueItem,
    MonthlyRevenueReportResponse,
    OccupancyReportResponse,
    PeriodSchema,
    ServiceTrendItem,
    ServiceTrendsReportResponse,
    ServiceUsageItem,
    ServiceUsageReportResponse,
)


class ReportService:
    """Business logic for generating SkyNest management reports."""

    def __init__(self, repo: Optional[ReportsRepo] = None) -> None:
        self.repo = repo or ReportsRepo()

    def get_occupancy_report(
        self,
        start_date: date,
        end_date: date,
        branch_id: Optional[int] = None,
    ) -> OccupancyReportResponse:
        data = self.repo.get_occupancy_data(start_date, end_date, branch_id)
        items = [BranchOccupancyItem(**b) for b in data]
        return OccupancyReportResponse(
            period=PeriodSchema(start_date=start_date, end_date=end_date),
            branches=items,
        )

    def get_guest_billing_report(
        self,
        payment_status: Optional[str] = None,
        branch_id: Optional[int] = None,
    ) -> GuestBillingReportResponse:
        data = self.repo.get_guest_billing_data(payment_status, branch_id)
        items = [GuestBillingItem(**b) for b in data]
        return GuestBillingReportResponse(data=items)

    def get_service_usage_report(
        self,
        branch_id: Optional[int] = None,
        service_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> ServiceUsageReportResponse:
        data = self.repo.get_service_usage_data(branch_id, service_id, start_date, end_date)
        items = [ServiceUsageItem(**s) for s in data]
        return ServiceUsageReportResponse(data=items)

    def get_monthly_revenue_report(
        self,
        year: int,
        branch_id: Optional[int] = None,
    ) -> MonthlyRevenueReportResponse:
        data = self.repo.get_monthly_revenue_data(year, branch_id)
        items = [MonthlyRevenueItem(**m) for m in data]
        return MonthlyRevenueReportResponse(year=year, data=items)

    def get_service_trends_report(
        self,
        limit: int = 5,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> ServiceTrendsReportResponse:
        data = self.repo.get_service_trends_data(limit, start_date, end_date)
        items = [ServiceTrendItem(**t) for t in data]
        period = (
            PeriodSchema(start_date=start_date, end_date=end_date)
            if (start_date and end_date)
            else None
        )
        return ServiceTrendsReportResponse(period=period, top_services=items)
