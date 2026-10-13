from unittest.mock import MagicMock

import pytest

from app.api.dependencies import get_current_user, get_report_service
from app.main import app
from app.schemas.auth import StaffUser
from app.schemas.reports import ServiceTrendsReportResponse


@pytest.mark.parametrize(
    "role,user_branch,requested_branch,expected_status,effective_branch",
    [
        ("admin", None, None, 200, None),
        ("admin", None, 2, 200, 2),
        ("receptionist", 1, None, 200, 1),
        ("receptionist", 1, 1, 200, 1),
        ("receptionist", 1, 2, 403, None),
    ],
)
def test_service_trends_branch_access(
    client, role, user_branch, requested_branch,
    expected_status, effective_branch,
):
    service = MagicMock()
    service.get_service_trends_report.return_value = (
        ServiceTrendsReportResponse(top_services=[])
    )
    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_report_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: StaffUser(
        staff_id=1, branch_id=user_branch, username="tester",
        full_name="Test Staff", role=role, is_active=True,
    )
    try:
        params = {"limit": 3}
        if requested_branch is not None:
            params["branch_id"] = requested_branch
        response = client.get(
            "/api/v1/private/reports/service-trends", params=params
        )
        assert response.status_code == expected_status
        if expected_status == 200:
            service.get_service_trends_report.assert_called_once_with(
                limit=3, branch_id=effective_branch
            )
        else:
            service.get_service_trends_report.assert_not_called()
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
