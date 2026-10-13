from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.repositories.reports_repo import ReportsRepo
from app.services.report_service import ReportService


@pytest.mark.parametrize("end", [date(2026, 10, 1), date(2026, 9, 30)])
def test_occupancy_rejects_invalid_period_before_query(end):
    repo = MagicMock(spec=ReportsRepo)
    service = ReportService(repo=repo)

    with pytest.raises(HTTPException) as error:
        service.get_occupancy_report(date(2026, 10, 1), end)

    assert error.value.status_code == 422
    repo.get_occupancy_data.assert_not_called()


def test_occupancy_accepts_valid_period():
    repo = MagicMock(spec=ReportsRepo)
    repo.get_occupancy_data.return_value = []
    service = ReportService(repo=repo)

    result = service.get_occupancy_report(
        date(2026, 10, 1), date(2026, 10, 2)
    )

    assert result.branches == []
    repo.get_occupancy_data.assert_called_once_with(
        date(2026, 10, 1), date(2026, 10, 2), None
    )
