def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    result = r.json()["data"]
    assert "items" in result
    assert "total" in result
    assert "page" in result
    assert "page_size" in result
    assert len(result["items"]) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200


def test_search_notes_with_pagination(client):
    # Create multiple notes
    for i in range(15):
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})

    # Test default pagination
    r = client.get("/notes/search/")
    assert r.status_code == 200
    data = r.json()["data"]
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
    data = r.json()["data"]
    assert data["page"] == 2
    assert len(data["items"]) == 5
    assert data["total"] == 15

    # Test custom page size
    r = client.get("/notes/search/", params={"page": 1, "page_size": 5})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["items"]) == 5
    assert data["total"] == 15
    assert data["page_size"] == 5

    # Test empty page
    r = client.get("/notes/search/", params={"page": 99, "page_size": 10})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["items"]) == 0
    assert data["total"] == 15


def test_search_notes_case_insensitive(client):
    client.post("/notes/", json={"title": "Hello World", "content": "Test content"})
    client.post("/notes/", json={"title": "hello world", "content": "Different content"})
    client.post("/notes/", json={"title": "HELLO WORLD", "content": "Another content"})

    # Case-insensitive search for "hello"
    r = client.get("/notes/search/", params={"q": "hello"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 3

    # Search in content
    r = client.get("/notes/search/", params={"q": "Different"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 1

    # Search with mixed case
    r = client.get("/notes/search/", params={"q": "HeLLo"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 3


def test_search_notes_sorting(client):
    # Create notes in specific order
    client.post("/notes/", json={"title": "Alpha", "content": "First"})
    client.post("/notes/", json={"title": "Beta", "content": "Second"})
    client.post("/notes/", json={"title": "Gamma", "content": "Third"})

    # Sort by title ascending
    r = client.get("/notes/search/", params={"sort": "title_asc"})
    assert r.status_code == 200
    data = r.json()["data"]
    titles = [item["title"] for item in data["items"]]
    assert titles == ["Alpha", "Beta", "Gamma"]

    # Sort by title descending
    r = client.get("/notes/search/", params={"sort": "title_desc"})
    assert r.status_code == 200
    data = r.json()["data"]
    titles = [item["title"] for item in data["items"]]
    assert titles == ["Gamma", "Beta", "Alpha"]


def test_search_notes_with_query(client):
    client.post("/notes/", json={"title": "Test", "content": "Hello world"})
    client.post("/notes/", json={"title": "Hello", "content": "Test world"})

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 2

    r = client.get("/notes/search/", params={"q": "Test"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 2


def test_search_notes_no_results(client):
    client.post("/notes/", json={"title": "Test", "content": "Hello world"})

    r = client.get("/notes/search/", params={"q": "nonexistent"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_search_notes_empty_query_returns_all(client):
    # Create a note
    client.post("/notes/", json={"title": "Test", "content": "Hello world"})

    r = client.get("/notes/search/", params={"q": ""})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] >= 1


def test_search_notes_invalid_sort(client):
    client.post("/notes/", json={"title": "Test", "content": "Hello world"})

    r = client.get("/notes/search/", params={"sort": "title_ascending"})
    assert r.status_code == 400
    assert "Invalid sort value" in r.json()["error"]["message"]

    r = client.get("/notes/search/", params={"sort": "invalid"})
    assert r.status_code == 400
    assert "Invalid sort value" in r.json()["error"]["message"]


def test_search_notes_invalid_pagination(client):
    client.post("/notes/", json={"title": "Test", "content": "Hello world"})

    # page=0 should fail
    r = client.get("/notes/search/", params={"page": 0})
    assert r.status_code == 400
    assert "page must be >= 1" in r.json()["error"]["message"]

    # page=-1 should fail
    r = client.get("/notes/search/", params={"page": -1})
    assert r.status_code == 400
    assert "page must be >= 1" in r.json()["error"]["message"]

    # page_size=0 should fail
    r = client.get("/notes/search/", params={"page_size": 0})
    assert r.status_code == 400
    assert "page_size must be > 0" in r.json()["error"]["message"]

    # page_size=-1 should fail
    r = client.get("/notes/search/", params={"page_size": -1})
    assert r.status_code == 400
    assert "page_size must be > 0" in r.json()["error"]["message"]

    # page_size > 100 should fail
    r = client.get("/notes/search/", params={"page_size": 101})
    assert r.status_code == 400
    assert "page_size must be <= 100" in r.json()["error"]["message"]

    # Very large page_size should fail
    r = client.get("/notes/search/", params={"page_size": 999999})
    assert r.status_code == 400
    assert "page_size must be <= 100" in r.json()["error"]["message"]


def test_create_note_validation_empty_title(client):
    r = client.post("/notes/", json={"title": "", "content": "Some content"})
    assert r.status_code == 422, r.text
    assert r.json()["ok"] is False
    assert "VALIDATION_ERROR" in r.json()["error"]["code"]


def test_create_note_validation_empty_content(client):
    r = client.post("/notes/", json={"title": "Some title", "content": ""})
    assert r.status_code == 422, r.text
    assert r.json()["ok"] is False


def test_create_note_validation_title_too_long(client):
    long_title = "x" * 501
    r = client.post("/notes/", json={"title": long_title, "content": "Some content"})
    assert r.status_code == 422, r.text
    assert r.json()["ok"] is False


def test_create_note_validation_content_too_long(client):
    long_content = "x" * 10001
    r = client.post("/notes/", json={"title": "Some title", "content": long_content})
    assert r.status_code == 422, r.text
    assert r.json()["ok"] is False


def test_update_note_validation_empty_title(client):
    client.post("/notes/", json={"title": "Original", "content": "Content"})
    r = client.put("/notes/1", json={"title": ""})
    assert r.status_code == 422, r.text
    assert r.json()["ok"] is False


def test_update_note_validation_title_too_long(client):
    client.post("/notes/", json={"title": "Original", "content": "Content"})
    long_title = "x" * 501
    r = client.put("/notes/1", json={"title": long_title})
    assert r.status_code == 422, r.text
    assert r.json()["ok"] is False


def test_update_note_validation_empty_content(client):
    client.post("/notes/", json={"title": "Original", "content": "Content"})
    r = client.put("/notes/1", json={"content": ""})
    assert r.status_code == 422, r.text
    assert r.json()["ok"] is False


def test_update_note_validation_content_too_long(client):
    client.post("/notes/", json={"title": "Original", "content": "Content"})
    long_content = "x" * 10001
    r = client.put("/notes/1", json={"content": long_content})
    assert r.status_code == 422, r.text
    assert r.json()["ok"] is False


def test_update_note_success(client):
    r = client.post("/notes/", json={"title": "Original", "content": "Content"})
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["title"] == "Updated"
    assert data["content"] == "Content"


def test_update_note_not_found(client):
    r = client.put("/notes/999", json={"title": "Updated"})
    assert r.status_code == 404, r.text
    assert r.json()["ok"] is False
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_delete_note_success(client):
    client.post("/notes/", json={"title": "To Delete", "content": "Content"})
    r = client.delete("/notes/1")
    assert r.status_code == 204, r.text
    r = client.get("/notes/1")
    assert r.status_code == 404, r.text
    assert r.json()["ok"] is False


def test_delete_note_not_found(client):
    r = client.delete("/notes/999")
    assert r.status_code == 404, r.text
    assert r.json()["ok"] is False


def test_extract_note_without_apply(client):
    """Test extraction without persisting (apply=false)."""
    # Create a note with hashtags and action items
    r = client.post(
        "/notes/",
        json={
            "title": "Test Note",
            "content": "This has #python and #testing tags\n- [ ] Write code\n- [ ] Review PR",
        },
    )
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Extract without applying
    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200
    data = r.json()["data"]
    assert "python" in data["hashtags"]
    assert "testing" in data["hashtags"]
    assert "Write code" in data["action_items"]
    assert "Review PR" in data["action_items"]


def test_extract_note_with_apply_creates_tags_and_action_items(client):
    """Test extraction with apply=true creates tags and action items."""
    # Create a note with hashtags and action items
    r = client.post(
        "/notes/",
        json={
            "title": "Test Note",
            "content": "This has #python and #testing tags\n- [ ] Write code\n- [ ] Review PR",
        },
    )
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Extract with applying
    r = client.post(f"/notes/{note_id}/extract", params={"apply": True})
    assert r.status_code == 200
    data = r.json()["data"]
    assert "python" in data["hashtags"]
    assert "testing" in data["hashtags"]
    assert "Write code" in data["action_items"]
    assert "Review PR" in data["action_items"]

    # Verify note now has tags attached
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note_data = r.json()["data"]
    tag_names = [tag["name"] for tag in note_data["tags"]]
    assert "python" in tag_names
    assert "testing" in tag_names

    # Verify action items were created
    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    descriptions = [item["description"] for item in items]
    assert "Write code" in descriptions
    assert "Review PR" in descriptions


def test_extract_note_not_found(client):
    """Test extraction on non-existent note."""
    r = client.post("/notes/999/extract")
    assert r.status_code == 404, r.text
    assert r.json()["ok"] is False


def test_extract_note_with_existing_tags(client):
    """Test extraction does not duplicate tags already on the note."""
    # Create a note with a tag already attached
    r = client.post("/notes/", json={"title": "Test", "content": "Content with #existing tag"})
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    # Attach the existing tag
    r = client.post(f"/notes/{note_id}/tags", json={"name": "existing"})
    assert r.status_code == 200

    # Extract with apply=true
    r = client.post(f"/notes/{note_id}/extract", params={"apply": True})
    assert r.status_code == 200

    # Verify note still has only one tag (not duplicated)
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note_data = r.json()["data"]
    tag_names = [tag["name"] for tag in note_data["tags"]]
    assert tag_names == ["existing"] or len(tag_names) == 1


def test_list_notes_pagination_empty_last_page(client):
    """Test that requesting a page beyond available data returns empty items."""
    # Create only 3 notes
    for i in range(3):
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})

    # Request page 99 (beyond available data)
    r = client.get("/notes/", params={"page": 99, "page_size": 10})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["items"] == []
    assert data["total"] == 3
    assert data["page"] == 99
    assert data["page_size"] == 10


def test_list_notes_pagination_too_large_page_size(client):
    """Test that page_size > 100 returns an error."""
    r = client.get("/notes/", params={"page": 1, "page_size": 101})
    assert r.status_code == 400
    assert "page_size must be <= 100" in r.json()["error"]["message"]


def test_list_notes_pagination_invalid_page(client):
    """Test that page < 1 returns an error."""
    r = client.get("/notes/", params={"page": 0})
    assert r.status_code == 400
    assert "page must be >= 1" in r.json()["error"]["message"]


def test_list_notes_pagination_custom_page_size(client):
    """Test pagination with custom page_size."""
    # Create 12 notes
    for i in range(12):
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"})

    # Page 1 with page_size=5
    r = client.get("/notes/", params={"page": 1, "page_size": 5})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["items"]) == 5
    assert data["total"] == 12
    assert data["page"] == 1
    assert data["page_size"] == 5

    # Page 3 should have 2 items (5+5+2=12)
    r = client.get("/notes/", params={"page": 3, "page_size": 5})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["items"]) == 2
    assert data["total"] == 12
    assert data["page"] == 3
