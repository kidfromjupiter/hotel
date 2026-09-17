from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────
# 1. Occupancy Report Schemas
# ─────────────────────────────────────────────
class PeriodSchema(BaseModel):
    start_date: date
    end_date: date


class BranchOccupancyItem(BaseModel):
    branch_name: str
    total_rooms: int
    occupied_nights: int
    total_possible_nights: int
    occupancy_rate_percent: float


class OccupancyReportResponse(BaseModel):
    period: PeriodSchema
    branches: List[BranchOccupancyItem]


# ─────────────────────────────────────────────
# 2. Guest Billing Report Schemas
# ─────────────────────────────────────────────
class GuestBillingItem(BaseModel):
    guest_name: str
    booking_id: int
    grand_total: float
    amount_paid: float
    outstanding_balance: float
    payment_status: str
    is_overdue: bool


class GuestBillingReportResponse(BaseModel):
    data: List[GuestBillingItem]


# ─────────────────────────────────────────────
# 3. Service Usage Report Schemas
# ─────────────────────────────────────────────
class ServiceUsageItem(BaseModel):
    service_name: str
    total_bookings_used: int
    total_days_used: int
    total_revenue: float


class ServiceUsageReportResponse(BaseModel):
    data: List[ServiceUsageItem]


# ─────────────────────────────────────────────
# 4. Monthly Revenue Report Schemas
# ─────────────────────────────────────────────
class MonthlyRevenueItem(BaseModel):
    branch_name: str
    month: str
    room_revenue: float
    service_revenue: float
    total_revenue: float


class MonthlyRevenueReportResponse(BaseModel):
    year: int
    data: List[MonthlyRevenueItem]


# ─────────────────────────────────────────────
# 5. Service Trends Report Schemas
# ─────────────────────────────────────────────
class ServiceTrendItem(BaseModel):
    rank: int
    service_name: str
    times_used: int
    total_revenue: float


class ServiceTrendsReportResponse(BaseModel):
    period: Optional[PeriodSchema] = None
    top_services: List[ServiceTrendItem]
