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


def test_complete_non_existent_item_returns_404(client):
    r = client.put("/action-items/9999/complete")
    assert r.status_code == 404
    assert r.json()["detail"] == "Action item not found"


def test_complete_already_completed_item(client):
    payload = {"description": "Test idempotency"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201
    item = r.json()

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    assert r.json()["completed"] is True

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    assert r.json()["completed"] is True


def test_multiple_items_workflow(client):
    r = client.post("/action-items/", json={"description": "First"})
    assert r.status_code == 201
    first = r.json()

    r = client.post("/action-items/", json={"description": "Second"})
    assert r.status_code == 201

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2

    r = client.put(f"/action-items/{first['id']}/complete")
    assert r.status_code == 200
    assert r.json()["completed"] is True

    r = client.get("/action-items/")
    items = r.json()
    assert len(items) == 2
    completed = [i for i in items if i["completed"]]
    assert len(completed) == 1
    assert completed[0]["description"] == "First"


def test_create_action_item_empty_description(client):
    payload = {"description": ""}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 422, r.text


def test_create_action_item_missing_description(client):
    payload = {}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 422, r.text
