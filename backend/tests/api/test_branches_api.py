def test_list_branches_public(client):
    res = client.get("/api/v1/public/branches/")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    branch_names = [b["branch_name"].lower() for b in data]
    assert "colombo" in branch_names
    assert "kandy" in branch_names
    assert "galle" in branch_names


def test_unprefixed_router_aliases_are_not_registered(client):
    assert client.get("/api/v1/branches/").status_code == 404
    assert client.get("/api/v1/reports/service-usage").status_code == 404
