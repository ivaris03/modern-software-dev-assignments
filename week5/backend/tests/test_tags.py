from backend.app.models import Note, Tag, note_tags


def test_create_and_list_tags(client):
    """Test creating and listing tags."""
    # Create a tag
    payload = {"name": "important"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "important"
    tag_id = data["id"]

    # List tags
    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    assert len(tags) >= 1
    assert any(t["name"] == "important" for t in tags)


def test_create_duplicate_tag(client):
    """Test that creating a duplicate tag returns 409."""
    payload = {"name": "duplicate"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201

    r = client.post("/tags/", json=payload)
    assert r.status_code == 409


def test_delete_tag(client):
    """Test deleting a tag."""
    # Create a tag
    payload = {"name": "to-delete"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201
    tag_id = r.json()["id"]

    # Delete the tag
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    # Verify it's gone
    r = client.get("/tags/")
    tags = r.json()
    assert not any(t["id"] == tag_id for t in tags)


def test_delete_tag_not_found(client):
    """Test deleting a non-existent tag returns 404."""
    r = client.delete("/tags/999")
    assert r.status_code == 404


def test_attach_tag_to_note(client):
    """Test attaching a tag to a note."""
    # Create a note
    note_payload = {"title": "Test Note", "content": "Hello world"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Attach a tag to the note
    tag_payload = {"name": "greeting"}
    r = client.post(f"/notes/{note_id}/tags", json=tag_payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert len(data["tags"]) >= 1
    assert any(t["name"] == "greeting" for t in data["tags"])


def test_attach_existing_tag_to_note(client):
    """Test attaching an existing tag to a note."""
    # Create a tag first
    tag_payload = {"name": "existing"}
    r = client.post("/tags/", json=tag_payload)
    assert r.status_code == 201
    tag_id = r.json()["id"]

    # Create a note
    note_payload = {"title": "Note with existing tag", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Attach the existing tag
    r = client.post(f"/notes/{note_id}/tags", json={"name": "existing"})
    assert r.status_code == 200
    data = r.json()
    assert any(t["id"] == tag_id for t in data["tags"])


def test_detach_tag_from_note(client):
    """Test detaching a tag from a note."""
    # Create a note with a tag
    note_payload = {"title": "Note to detach", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Attach a tag
    r = client.post(f"/notes/{note_id}/tags", json={"name": "detach-me"})
    assert r.status_code == 200
    tag_id = r.json()["tags"][0]["id"]

    # Detach the tag
    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 204

    # Verify tag is detached
    r = client.get(f"/notes/{note_id}")
    data = r.json()
    assert not any(t["id"] == tag_id for t in data["tags"])


def test_detach_tag_not_found(client):
    """Test detaching a non-existent tag from a note returns 404."""
    # Create a note
    note_payload = {"title": "Note", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Try to detach non-existent tag
    r = client.delete(f"/notes/{note_id}/tags/999")
    assert r.status_code == 404


def test_attach_tag_to_nonexistent_note(client):
    """Test attaching a tag to a non-existent note returns 404."""
    r = client.post("/notes/999/tags", json={"name": "orphan"})
    assert r.status_code == 404


def test_note_with_tags_in_list(client):
    """Test that notes with tags are returned correctly in list."""
    # Create a note with tags
    note_payload = {"title": "Note with tags", "content": "Content"}
    r = client.post("/notes/", json=note_payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Attach two tags
    r = client.post(f"/notes/{note_id}/tags", json={"name": "tag1"})
    r = client.post(f"/notes/{note_id}/tags", json={"name": "tag2"})

    # List notes and verify tags are included
    r = client.get("/notes/")
    assert r.status_code == 200
    notes = r.json()
    note = next((n for n in notes if n["id"] == note_id), None)
    assert note is not None
    tag_names = [t["name"] for t in note["tags"]]
    assert "tag1" in tag_names
    assert "tag2" in tag_names


def test_tag_model_relation(client):
    """Test the many-to-many relationship between Note and Tag."""
    # Create two notes
    r = client.post("/notes/", json={"title": "Note 1", "content": "Content 1"})
    note1_id = r.json()["id"]
    r = client.post("/notes/", json={"title": "Note 2", "content": "Content 2"})
    note2_id = r.json()["id"]

    # Create a tag
    r = client.post("/tags/", json={"name": "shared"})
    assert r.status_code == 201
    tag_id = r.json()["id"]

    # Attach tag to both notes
    r = client.post(f"/notes/{note1_id}/tags", json={"name": "shared"})
    r = client.post(f"/notes/{note2_id}/tags", json={"name": "shared"})

    # Verify the tag is attached to both notes
    r = client.get(f"/notes/{note1_id}")
    assert any(t["id"] == tag_id for t in r.json()["tags"])

    r = client.get(f"/notes/{note2_id}")
    assert any(t["id"] == tag_id for t in r.json()["tags"])

    # Verify tag appears in both notes' tag lists
    r = client.get("/notes/")
    notes = r.json()
    note1 = next((n for n in notes if n["id"] == note1_id), None)
    note2 = next((n for n in notes if n["id"] == note2_id), None)
    assert any(t["id"] == tag_id for t in note1["tags"])
    assert any(t["id"] == tag_id for t in note2["tags"])


def test_note_search_returns_tags(client):
    """Test that note search endpoint returns tags with notes."""
    # Create a note with tags
    r = client.post("/notes/", json={"title": "Searchable Note", "content": "Content"})
    note_id = r.json()["id"]
    r = client.post(f"/notes/{note_id}/tags", json={"name": "searchable"})

    # Search for the note
    r = client.get("/notes/search/", params={"q": "Searchable"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    note = next((n for n in data["items"] if n["id"] == note_id), None)
    assert note is not None
    assert any(t["name"] == "searchable" for t in note["tags"])
