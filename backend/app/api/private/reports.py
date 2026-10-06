from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import (
    get_report_service,
    get_current_user,
    enforce_branch_access,
)
from app.schemas.auth import StaffUser
from app.schemas.reports import (
    GuestBillingReportResponse,
    MonthlyRevenueReportResponse,
    OccupancyReportResponse,
    ServiceTrendsReportResponse,
    ServiceUsageReportResponse,
)
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/occupancy", response_model=OccupancyReportResponse)
def get_occupancy_report(
    start_date: date = Query(..., description="Period start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Period end date (YYYY-MM-DD)"),
    branch_id: Optional[int] = Query(None, description="Optional branch ID filter"),
    report_service: ReportService = Depends(get_report_service),
    current_user: StaffUser = Depends(get_current_user),
):
    """Calculates room occupancy rate per branch over a requested period."""
    effective_branch = enforce_branch_access(branch_id, current_user)
    return report_service.get_occupancy_report(
        start_date=start_date,
        end_date=end_date,
        branch_id=effective_branch,
    )


@router.get("/guest-billing", response_model=GuestBillingReportResponse)
def get_guest_billing_report(
    payment_status: Optional[str] = Query(
        None, description="Filter: PAID, PARTIAL, or UNPAID"
    ),
    branch_id: Optional[int] = Query(None, description="Optional branch ID filter"),
    report_service: ReportService = Depends(get_report_service),
    current_user: StaffUser = Depends(get_current_user),
):
    """Returns guest billing summaries, outstanding balances, and overdue flags."""
    effective_branch = enforce_branch_access(branch_id, current_user)
    return report_service.get_guest_billing_report(
        payment_status=payment_status,
        branch_id=effective_branch,
    )


@router.get("/service-usage", response_model=ServiceUsageReportResponse)
def get_service_usage_report(
    branch_id: Optional[int] = Query(None, description="Optional branch ID filter"),
    report_service: ReportService = Depends(get_report_service),
    current_user: StaffUser = Depends(get_current_user),
):
    """Returns total revenue and usage count for each additional service."""
    effective_branch = enforce_branch_access(branch_id, current_user)
    return report_service.get_service_usage_report(branch_id=effective_branch)


@router.get("/monthly-revenue", response_model=MonthlyRevenueReportResponse)
def get_monthly_revenue_report(
    year: int = Query(..., description="Reporting year (e.g. 2026)"),
    branch_id: Optional[int] = Query(None, description="Optional branch ID filter"),
    report_service: ReportService = Depends(get_report_service),
    current_user: StaffUser = Depends(get_current_user),
):
    """Returns month-by-month revenue broken down into room and service revenue."""
    effective_branch = enforce_branch_access(branch_id, current_user)
    return report_service.get_monthly_revenue_report(
        year=year,
        branch_id=effective_branch,
    )


@router.get("/service-trends", response_model=ServiceTrendsReportResponse)
def get_service_trends_report(
    limit: int = Query(5, ge=1, le=20, description="Number of top services to return"),
    report_service: ReportService = Depends(get_report_service),
):
    """Returns the top N most utilized services ranked by total booking count."""
    return report_service.get_service_trends_report(
        limit=limit,
    )

