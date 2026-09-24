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


def test_list_branches_alias(client):
    res = client.get("/api/v1/branches/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3


def test_get_amenities_public_branches(client):
    # Test Colombo
    res_colombo = client.get("/api/v1/public/amenities?branch=colombo")
    assert res_colombo.status_code == 200
    data_colombo = res_colombo.json()
    assert "amenities" in data_colombo
    assert len(data_colombo["amenities"]) > 0

    # Test Kandy
    res_kandy = client.get("/api/v1/public/amenities?branch=kandy")
    assert res_kandy.status_code == 200
    data_kandy = res_kandy.json()
    assert "amenities" in data_kandy
    assert len(data_kandy["amenities"]) > 0

    # Test Galle
    res_galle = client.get("/api/v1/public/amenities?branch=galle")
    assert res_galle.status_code == 200
    data_galle = res_galle.json()
    assert "amenities" in data_galle
    assert len(data_galle["amenities"]) > 0


def test_get_amenities_alias(client):
    res = client.get("/api/v1/amenities?branch=colombo")
    assert res.status_code == 200
    data = res.json()
    assert "amenities" in data
    assert len(data["amenities"]) > 0
