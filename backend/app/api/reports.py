from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_report_service
from app.schemas.reports import (
    GuestBillingReportResponse,
    MonthlyRevenueReportResponse,
    OccupancyReportResponse,
    ServiceTrendsReportResponse,
    ServiceUsageReportResponse,
)
from app.services.report_service import ReportService

router = APIRouter()


# ─────────────────────────────────────────────
# 1. Report 1 — Room Occupancy Rate
# ─────────────────────────────────────────────
@router.get("/occupancy", response_model=OccupancyReportResponse)
def get_occupancy_report(
    start_date: date = Query(..., description="Period start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Period end date (YYYY-MM-DD)"),
    branch_id: Optional[int] = Query(None, description="Optional branch ID filter"),
    report_service: ReportService = Depends(get_report_service),
):
    """Calculates room occupancy rate per branch over a requested period."""
    return report_service.get_occupancy_report(
        start_date=start_date,
        end_date=end_date,
        branch_id=branch_id,
    )


# ─────────────────────────────────────────────
# 2. Report 2 — Guest Billing Summary
# ─────────────────────────────────────────────
@router.get("/guest-billing", response_model=GuestBillingReportResponse)
def get_guest_billing_report(
    payment_status: Optional[str] = Query(
        None, description="Filter: PAID, PARTIAL, or UNPAID"
    ),
    branch_id: Optional[int] = Query(None, description="Optional branch ID filter"),
    report_service: ReportService = Depends(get_report_service),
):
    """Returns guest billing summaries, outstanding balances, and overdue flags."""
    return report_service.get_guest_billing_report(
        payment_status=payment_status,
        branch_id=branch_id,
    )


# ─────────────────────────────────────────────
# 3. Report 3 — Service Usage Breakdown
# ─────────────────────────────────────────────
@router.get("/service-usage", response_model=ServiceUsageReportResponse)
def get_service_usage_report(
    branch_id: Optional[int] = Query(None, description="Optional branch ID filter"),
    service_id: Optional[int] = Query(None, description="Optional service ID filter"),
    start_date: Optional[date] = Query(None, description="Period start date"),
    end_date: Optional[date] = Query(None, description="Period end date"),
    report_service: ReportService = Depends(get_report_service),
):
    """Breakdown of add-on and guest services used per branch and type."""
    return report_service.get_service_usage_report(
        branch_id=branch_id,
        service_id=service_id,
        start_date=start_date,
        end_date=end_date,
    )


# ─────────────────────────────────────────────
# 4. Report 4 — Monthly Revenue Breakdown
# ─────────────────────────────────────────────
@router.get("/monthly-revenue", response_model=MonthlyRevenueReportResponse)
def get_monthly_revenue_report(
    year: int = Query(..., description="Reporting year (e.g. 2026)"),
    branch_id: Optional[int] = Query(None, description="Optional branch ID filter"),
    report_service: ReportService = Depends(get_report_service),
):
    """Returns monthly revenue breakdown (room charges + services) per branch."""
    return report_service.get_monthly_revenue_report(
        year=year,
        branch_id=branch_id,
    )


# ─────────────────────────────────────────────
# 5. Report 5 — Service Usage Trends
# ─────────────────────────────────────────────
@router.get("/service-trends", response_model=ServiceTrendsReportResponse)
def get_service_trends_report(
    limit: int = Query(5, description="Number of top services to return"),
    start_date: Optional[date] = Query(None, description="Period start date"),
    end_date: Optional[date] = Query(None, description="Period end date"),
    report_service: ReportService = Depends(get_report_service),
):
    """Ranks top-used services and customer preferences descending by frequency."""
    return report_service.get_service_trends_report(
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )
