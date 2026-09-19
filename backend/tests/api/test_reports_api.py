def test_get_occupancy_report(client):
    response = client.get(
        "/api/v1/reports/occupancy?start_date=2026-10-01&end_date=2026-10-31"
    )
    assert response.status_code == 200
    data = response.json()
    assert "period" in data
    assert "branches" in data
    assert len(data["branches"]) >= 1
    branch = data["branches"][0]
    assert "branch_name" in branch
    assert "occupancy_rate_percent" in branch


def test_get_guest_billing_report(client):
    response = client.get("/api/v1/reports/guest-billing?payment_status=PARTIAL")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    for item in data["data"]:
        assert item["payment_status"] == "PARTIAL"
        assert "outstanding_balance" in item
        assert "is_overdue" in item


def test_get_service_usage_report(client):
    response = client.get("/api/v1/reports/service-usage")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) >= 1
    item = data["data"][0]
    assert "service_name" in item
    assert "total_revenue" in item


def test_get_monthly_revenue_report(client):
    response = client.get("/api/v1/reports/monthly-revenue?year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == 2026
    assert "data" in data
    assert len(data["data"]) >= 1
    month_item = data["data"][0]
    assert "room_revenue" in month_item
    assert "service_revenue" in month_item
    assert (
        month_item["total_revenue"]
        == month_item["room_revenue"] + month_item["service_revenue"]
    )


def test_get_service_trends_report(client):
    response = client.get("/api/v1/reports/service-trends?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert "top_services" in data
    assert len(data["top_services"]) <= 3
    if data["top_services"]:
        assert data["top_services"][0]["rank"] == 1
