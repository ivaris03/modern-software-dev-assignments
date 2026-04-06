def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_list_filter_by_completed_false(client):
    r = client.post("/action-items/", json={"description": "Open item"})
    assert r.status_code == 201
    item1 = r.json()

    r = client.post("/action-items/", json={"description": "Another open"})
    assert r.status_code == 201

    r = client.put(f"/action-items/{item1['id']}/complete")
    assert r.status_code == 200

    r = client.get("/action-items/?completed=false")
    assert r.status_code == 200
    items = r.json()
    assert all(i["completed"] is False for i in items)
    assert len(items) == 1

    r = client.get("/action-items/?completed=true")
    assert r.status_code == 200
    items = r.json()
    assert all(i["completed"] is True for i in items)
    assert len(items) == 1


def test_list_filter_all(client):
    r = client.post("/action-items/", json={"description": "Item 1"})
    assert r.status_code == 201
    r = client.post("/action-items/", json={"description": "Item 2"})
    assert r.status_code == 201

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2


def test_bulk_complete(client):
    r = client.post("/action-items/", json={"description": "Bulk 1"})
    item1 = r.json()
    r = client.post("/action-items/", json={"description": "Bulk 2"})
    item2 = r.json()
    r = client.post("/action-items/", json={"description": "Bulk 3"})
    item3 = r.json()

    r = client.post("/action-items/bulk-complete", json={"ids": [item1["id"], item2["id"]]})
    assert r.status_code == 200
    completed = r.json()
    assert len(completed) == 2
    assert all(i["completed"] is True for i in completed)

    r = client.get("/action-items/")
    items = r.json()
    completed_items = [i for i in items if i["id"] in [item1["id"], item2["id"]]]
    open_items = [i for i in items if i["id"] == item3["id"]]
    assert all(i["completed"] is True for i in completed_items)
    assert all(i["completed"] is False for i in open_items)


def test_bulk_complete_partial_not_found(client):
    r = client.post("/action-items/", json={"description": "Real item"})
    item = r.json()

    r = client.post("/action-items/bulk-complete", json={"ids": [item["id"], 9999]})
    assert r.status_code == 404
    assert "9999" in r.json()["detail"]


def test_bulk_complete_empty_ids(client):
    r = client.post("/action-items/bulk-complete", json={"ids": []})
    assert r.status_code == 200
    assert r.json() == []


def test_bulk_complete_rollback_on_nonexistent(client):
    """Verify transactional behavior: if any ID doesn't exist, nothing is marked complete."""
    r = client.post("/action-items/", json={"description": "Should stay open"})
    item = r.json()

    r = client.post("/action-items/bulk-complete", json={"ids": [item["id"], 99999]})
    assert r.status_code == 404

    r = client.get("/action-items/")
    items = r.json()
    item_after = next(i for i in items if i["id"] == item["id"])
    assert item_after["completed"] is False
