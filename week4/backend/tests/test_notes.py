def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_update_note(client):
    payload = {"title": "Original", "content": "Original content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    update_payload = {"title": "Updated", "content": "Updated content"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["title"] == "Updated"
    assert data["content"] == "Updated content"


def test_update_note_not_found(client):
    update_payload = {"title": "Updated", "content": "Updated content"}
    r = client.put("/notes/99999", json=update_payload)
    assert r.status_code == 404, r.text


def test_delete_note(client):
    payload = {"title": "ToDelete", "content": "Will be deleted"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204, r.text

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404, r.text


def test_delete_note_not_found(client):
    r = client.delete("/notes/99999")
    assert r.status_code == 404, r.text


def test_create_note_empty_title(client):
    payload = {"title": "", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422, r.text


def test_create_note_empty_content(client):
    payload = {"title": "Test", "content": ""}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422, r.text


def test_create_note_missing_title(client):
    payload = {"content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422, r.text


def test_create_note_missing_content(client):
    payload = {"title": "Test"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 422, r.text


def test_update_note_empty_title(client):
    payload = {"title": "Valid", "content": "Valid content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    update_payload = {"title": "", "content": "Updated content"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 422, r.text


def test_update_note_empty_content(client):
    payload = {"title": "Valid", "content": "Valid content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    update_payload = {"title": "Updated", "content": ""}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 422, r.text
