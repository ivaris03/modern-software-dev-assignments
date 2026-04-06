def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()["data"]
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()["data"]
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    result = r.json()["data"]
    assert "items" in result
    items = result["items"]
    assert len(items) == 1


def test_list_filter_by_completed_false(client):
    r = client.post("/action-items/", json={"description": "Open item"})
    assert r.status_code == 201
    item1 = r.json()["data"]

    r = client.post("/action-items/", json={"description": "Another open"})
    assert r.status_code == 201

    r = client.put(f"/action-items/{item1['id']}/complete")
    assert r.status_code == 200

    r = client.get("/action-items/?completed=false")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert all(i["completed"] is False for i in items)
    assert len(items) == 1

    r = client.get("/action-items/?completed=true")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert all(i["completed"] is True for i in items)
    assert len(items) == 1


def test_list_filter_all(client):
    r = client.post("/action-items/", json={"description": "Item 1"})
    assert r.status_code == 201
    r = client.post("/action-items/", json={"description": "Item 2"})
    assert r.status_code == 201

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert len(items) == 2


def test_bulk_complete(client):
    r = client.post("/action-items/", json={"description": "Bulk 1"})
    item1 = r.json()["data"]
    r = client.post("/action-items/", json={"description": "Bulk 2"})
    item2 = r.json()["data"]
    r = client.post("/action-items/", json={"description": "Bulk 3"})
    item3 = r.json()["data"]

    r = client.post("/action-items/bulk-complete", json={"ids": [item1["id"], item2["id"]]})
    assert r.status_code == 200
    completed = r.json()["data"]
    assert len(completed) == 2
    assert all(i["completed"] is True for i in completed)

    r = client.get("/action-items/")
    items = r.json()["data"]["items"]
    completed_items = [i for i in items if i["id"] in [item1["id"], item2["id"]]]
    open_items = [i for i in items if i["id"] == item3["id"]]
    assert all(i["completed"] is True for i in completed_items)
    assert all(i["completed"] is False for i in open_items)


def test_bulk_complete_partial_not_found(client):
    r = client.post("/action-items/", json={"description": "Real item"})
    item = r.json()["data"]

    r = client.post("/action-items/bulk-complete", json={"ids": [item["id"], 9999]})
    assert r.status_code == 404
    assert "9999" in r.json()["error"]["message"]


def test_bulk_complete_empty_ids(client):
    r = client.post("/action-items/bulk-complete", json={"ids": []})
    assert r.status_code == 200
    assert r.json()["data"] == []


def test_bulk_complete_rollback_on_nonexistent(client):
    """Verify transactional behavior: if any ID doesn't exist, nothing is marked complete."""
    r = client.post("/action-items/", json={"description": "Should stay open"})
    item = r.json()["data"]

    r = client.post("/action-items/bulk-complete", json={"ids": [item["id"], 99999]})
    assert r.status_code == 404

    r = client.get("/action-items/")
    items = r.json()["data"]["items"]
    item_after = next(i for i in items if i["id"] == item["id"])
    assert item_after["completed"] is False


def test_list_action_items_pagination_empty_last_page(client):
    """Test that requesting a page beyond available data returns empty items."""
    # Create only 3 action items
    for i in range(3):
        client.post("/action-items/", json={"description": f"Action {i}"})

    # Request page 99 (beyond available data)
    r = client.get("/action-items/", params={"page": 99, "page_size": 10})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["items"] == []
    assert data["total"] == 3
    assert data["page"] == 99
    assert data["page_size"] == 10


def test_list_action_items_pagination_too_large_page_size(client):
    """Test that page_size > 100 returns an error."""
    r = client.get("/action-items/", params={"page": 1, "page_size": 101})
    assert r.status_code == 400
    assert "page_size must be <= 100" in r.json()["error"]["message"]


def test_list_action_items_pagination_invalid_page(client):
    """Test that page < 1 returns an error."""
    r = client.get("/action-items/", params={"page": 0})
    assert r.status_code == 400
    assert "page must be >= 1" in r.json()["error"]["message"]


def test_list_action_items_pagination_custom_page_size(client):
    """Test pagination with custom page_size."""
    # Create 7 action items
    for i in range(7):
        client.post("/action-items/", json={"description": f"Action {i}"})

    # Page 1 with page_size=3
    r = client.get("/action-items/", params={"page": 1, "page_size": 3})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["items"]) == 3
    assert data["total"] == 7
    assert data["page"] == 1
    assert data["page_size"] == 3

    # Page 3 should have 1 item (3+3+1=7)
    r = client.get("/action-items/", params={"page": 3, "page_size": 3})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["items"]) == 1
    assert data["total"] == 7
    assert data["page"] == 3
