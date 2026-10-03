from datetime import date
from unittest.mock import MagicMock

from app.repositories.reports_repo import ReportsRepo
from app.services.report_service import ReportService


def test_reports_repo_calls_db_functions():
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_db.cursor.return_value.__enter__.return_value = mock_cursor

    # 1. Occupancy report
    mock_cursor.fetchone.return_value = {
        "get_occupancy_report": [
            {
                "branch_name": "Colombo",
                "total_rooms": 20,
                "occupied_nights": 150,
                "total_possible_nights": 600,
                "occupancy_rate_percent": 25.0,
            }
        ]
    }
    repo = ReportsRepo(db=mock_db)
    occ = repo.get_occupancy_data(date(2026, 10, 1), date(2026, 10, 31), branch_id=1)
    assert len(occ) == 1
    assert occ[0]["branch_name"] == "Colombo"
    assert "get_occupancy_report" in mock_cursor.execute.call_args[0][0]

    # 2. Guest billing report
    mock_cursor.fetchone.return_value = {
        "get_guest_billing_report": [
            {
                "guest_name": "Amal",
                "booking_id": 500001,
                "grand_total": 50000.0,
                "amount_paid": 50000.0,
                "outstanding_balance": 0.0,
                "payment_status": "PAID",
                "is_overdue": False,
            }
        ]
    }
    billing = repo.get_guest_billing_data(payment_status="PAID")
    assert len(billing) == 1
    assert "get_guest_billing_report" in mock_cursor.execute.call_args[0][0]

    # 3. Service usage report
    mock_cursor.fetchone.return_value = {
        "get_service_usage_report": [
            {
                "service_name": "Spa",
                "total_bookings_used": 10,
                "total_days_used": 10,
                "total_revenue": 75000.0,
            }
        ]
    }
    usage = repo.get_service_usage_data()
    assert len(usage) == 1
    assert "get_service_usage_report" in mock_cursor.execute.call_args[0][0]

    # 4. Monthly revenue report
    mock_cursor.fetchone.return_value = {
        "get_monthly_revenue_report": [
            {
                "branch_name": "Colombo",
                "month": "October",
                "room_revenue": 500000.0,
                "service_revenue": 100000.0,
                "total_revenue": 600000.0,
            }
        ]
    }
    monthly = repo.get_monthly_revenue_data(year=2026)
    assert len(monthly) == 1
    assert "get_monthly_revenue_report" in mock_cursor.execute.call_args[0][0]

    # 5. Service trends report
    mock_cursor.fetchone.return_value = {
        "get_service_trends_report": [
            {
                "rank": 1,
                "service_name": "Airport Transfer",
                "times_used": 50,
                "total_revenue": 250000.0,
            }
        ]
    }
    trends = repo.get_service_trends_data(limit=1)
    assert len(trends) == 1
    assert "get_service_trends_report" in mock_cursor.execute.call_args[0][0]


def test_report_service_with_injected_repo():
    mock_repo = MagicMock(spec=ReportsRepo)
    mock_repo.get_occupancy_data.return_value = [
        {
            "branch_name": "Colombo",
            "total_rooms": 10,
            "occupied_nights": 5,
            "total_possible_nights": 100,
            "occupancy_rate_percent": 5.0,
        }
    ]

    service = ReportService(repo=mock_repo)
    res = service.get_occupancy_report(date(2026, 10, 1), date(2026, 10, 10))
    assert len(res.branches) == 1
    assert res.branches[0].branch_name == "Colombo"
    mock_repo.get_occupancy_data.assert_called_once()
