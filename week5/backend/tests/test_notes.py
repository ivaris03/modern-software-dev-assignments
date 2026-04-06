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


def test_search_notes_with_pagination(client):
    # Create multiple notes
    for i in range(15):
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})

    # Test default pagination
    r = client.get("/notes/search/")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) == 10
    assert data["total"] == 15

    # Test second page
    r = client.get("/notes/search/", params={"page": 2, "page_size": 10})
    assert r.status_code == 200
    data = r.json()
    assert data["page"] == 2
    assert len(data["items"]) == 5
    assert data["total"] == 15

    # Test custom page size
    r = client.get("/notes/search/", params={"page": 1, "page_size": 5})
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 5
    assert data["total"] == 15
    assert data["page_size"] == 5

    # Test empty page
    r = client.get("/notes/search/", params={"page": 99, "page_size": 10})
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 0
    assert data["total"] == 15


def test_search_notes_case_insensitive(client):
    client.post("/notes/", json={"title": "Hello World", "content": "Test content"})
    client.post("/notes/", json={"title": "hello world", "content": "Different content"})
    client.post("/notes/", json={"title": "HELLO WORLD", "content": "Another content"})

    # Case-insensitive search for "hello"
    r = client.get("/notes/search/", params={"q": "hello"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3

    # Search in content
    r = client.get("/notes/search/", params={"q": "Different"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1

    # Search with mixed case
    r = client.get("/notes/search/", params={"q": "HeLLo"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3


def test_search_notes_sorting(client):
    # Create notes in specific order
    client.post("/notes/", json={"title": "Alpha", "content": "First"})
    client.post("/notes/", json={"title": "Beta", "content": "Second"})
    client.post("/notes/", json={"title": "Gamma", "content": "Third"})

    # Sort by title ascending
    r = client.get("/notes/search/", params={"sort": "title_asc"})
    assert r.status_code == 200
    data = r.json()
    titles = [item["title"] for item in data["items"]]
    assert titles == ["Alpha", "Beta", "Gamma"]

    # Sort by title descending
    r = client.get("/notes/search/", params={"sort": "title_desc"})
    assert r.status_code == 200
    data = r.json()
    titles = [item["title"] for item in data["items"]]
    assert titles == ["Gamma", "Beta", "Alpha"]


def test_search_notes_with_query(client):
    client.post("/notes/", json={"title": "Test", "content": "Hello world"})
    client.post("/notes/", json={"title": "Hello", "content": "Test world"})

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2

    r = client.get("/notes/search/", params={"q": "Test"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2


def test_search_notes_no_results(client):
    client.post("/notes/", json={"title": "Test", "content": "Hello world"})

    r = client.get("/notes/search/", params={"q": "nonexistent"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_search_notes_empty_query_returns_all(client):
    # Create a note
    client.post("/notes/", json={"title": "Test", "content": "Hello world"})

    r = client.get("/notes/search/", params={"q": ""})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1


def test_search_notes_invalid_sort(client):
    client.post("/notes/", json={"title": "Test", "content": "Hello world"})

    r = client.get("/notes/search/", params={"sort": "title_ascending"})
    assert r.status_code == 400
    assert "Invalid sort value" in r.json()["detail"]

    r = client.get("/notes/search/", params={"sort": "invalid"})
    assert r.status_code == 400
    assert "Invalid sort value" in r.json()["detail"]


def test_search_notes_invalid_pagination(client):
    client.post("/notes/", json={"title": "Test", "content": "Hello world"})

    # page=0 should fail
    r = client.get("/notes/search/", params={"page": 0})
    assert r.status_code == 400
    assert "page must be >= 1" in r.json()["detail"]

    # page=-1 should fail
    r = client.get("/notes/search/", params={"page": -1})
    assert r.status_code == 400
    assert "page must be >= 1" in r.json()["detail"]

    # page_size=0 should fail
    r = client.get("/notes/search/", params={"page_size": 0})
    assert r.status_code == 400
    assert "page_size must be > 0" in r.json()["detail"]

    # page_size=-1 should fail
    r = client.get("/notes/search/", params={"page_size": -1})
    assert r.status_code == 400
    assert "page_size must be > 0" in r.json()["detail"]

    # page_size > 100 should fail
    r = client.get("/notes/search/", params={"page_size": 101})
    assert r.status_code == 400
    assert "page_size must be <= 100" in r.json()["detail"]

    # Very large page_size should fail
    r = client.get("/notes/search/", params={"page_size": 999999})
    assert r.status_code == 400
    assert "page_size must be <= 100" in r.json()["detail"]


def test_create_note_validation_empty_title(client):
    r = client.post("/notes/", json={"title": "", "content": "Some content"})
    assert r.status_code == 422, r.text


def test_create_note_validation_empty_content(client):
    r = client.post("/notes/", json={"title": "Some title", "content": ""})
    assert r.status_code == 422, r.text


def test_create_note_validation_title_too_long(client):
    long_title = "x" * 501
    r = client.post("/notes/", json={"title": long_title, "content": "Some content"})
    assert r.status_code == 422, r.text


def test_create_note_validation_content_too_long(client):
    long_content = "x" * 10001
    r = client.post("/notes/", json={"title": "Some title", "content": long_content})
    assert r.status_code == 422, r.text


def test_update_note_validation_empty_title(client):
    client.post("/notes/", json={"title": "Original", "content": "Content"})
    r = client.put("/notes/1", json={"title": ""})
    assert r.status_code == 422, r.text


def test_update_note_validation_title_too_long(client):
    client.post("/notes/", json={"title": "Original", "content": "Content"})
    long_title = "x" * 501
    r = client.put("/notes/1", json={"title": long_title})
    assert r.status_code == 422, r.text


def test_update_note_validation_empty_content(client):
    client.post("/notes/", json={"title": "Original", "content": "Content"})
    r = client.put("/notes/1", json={"content": ""})
    assert r.status_code == 422, r.text


def test_update_note_validation_content_too_long(client):
    client.post("/notes/", json={"title": "Original", "content": "Content"})
    long_content = "x" * 10001
    r = client.put("/notes/1", json={"content": long_content})
    assert r.status_code == 422, r.text


def test_update_note_success(client):
    r = client.post("/notes/", json={"title": "Original", "content": "Content"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["title"] == "Updated"
    assert data["content"] == "Content"


def test_update_note_not_found(client):
    r = client.put("/notes/999", json={"title": "Updated"})
    assert r.status_code == 404, r.text


def test_delete_note_success(client):
    client.post("/notes/", json={"title": "To Delete", "content": "Content"})
    r = client.delete("/notes/1")
    assert r.status_code == 204, r.text
    r = client.get("/notes/1")
    assert r.status_code == 404, r.text


def test_delete_note_not_found(client):
    r = client.delete("/notes/999")
    assert r.status_code == 404, r.text
