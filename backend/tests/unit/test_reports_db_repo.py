from datetime import date
from unittest.mock import MagicMock

from app.repositories.reports_repo import ReportsRepo
from app.services.report_service import ReportService


def test_reports_repo_runs_aggregate_queries():
    mock_db = MagicMock()
    cursor = mock_db.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [{"branch_name": "colombo", "total_rooms": 20}]
    repo = ReportsRepo(db=mock_db)

    assert repo.get_occupancy_data(date(2026, 10, 1), date(2026, 10, 31), 1)[0]["total_rooms"] == 20
    assert "WITH room_counts AS" in cursor.execute.call_args.args[0]
    repo.get_guest_billing_data(payment_status="PAID")
    assert "FROM booking bk" in cursor.execute.call_args.args[0]
    repo.get_service_usage_data(branch_id=1)
    assert "COUNT(DISTINCT sc.booking_id)" in cursor.execute.call_args.args[0]
    repo.get_monthly_revenue_data(year=2026)
    assert "SUM(t.amount)" in cursor.execute.call_args.args[0]
    repo.get_service_trends_data(limit=1)
    assert "ROW_NUMBER() OVER" in cursor.execute.call_args.args[0]


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
