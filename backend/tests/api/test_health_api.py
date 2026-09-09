def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "SkyNest Hotels API" in data["message"]


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_branches_endpoint(client):
    response = client.get("/api/v1/branches/")
    assert response.status_code == 200
    branches = response.json()
    assert len(branches) == 3
    branch_names = [b["branch_name"] for b in branches]
    assert "Colombo" in branch_names
    assert "Kandy" in branch_names
    assert "Galle" in branch_names
