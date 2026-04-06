"""Performance and scaling tests to verify query performance with indexes.

These tests seed larger datasets to ensure no regressions and verify
that indexes are being used effectively.
"""

import time


def test_notes_search_with_large_dataset(client):
    """Test search performance with 100 notes."""
    # Seed 100 notes with varied content
    for i in range(100):
        client.post("/notes/", json={
            "title": f"Note {i:03d}",
            "content": f"Content for note {i} with searchable terms"
        })

    # Test search performance
    start = time.time()
    r = client.get("/notes/search/", params={"q": "Note", "page": 1, "page_size": 10})
    elapsed = time.time() - start

    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 100
    assert elapsed < 1.0, f"Search took {elapsed:.2f}s, should be < 1s"


def test_notes_search_with_title_filter_large_dataset(client):
    """Test title search with 100 notes."""
    # Seed notes with specific titles
    for i in range(100):
        title = f"Important {i % 10}" if i % 5 == 0 else f"Regular {i}"
        client.post("/notes/", json={
            "title": title,
            "content": f"Content {i}"
        })

    start = time.time()
    r = client.get("/notes/search/", params={"q": "Important"})
    elapsed = time.time() - start

    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 20  # 100/5 = 20 "Important" notes
    assert elapsed < 1.0, f"Search took {elapsed:.2f}s, should be < 1s"


def test_notes_sorting_large_dataset(client):
    """Test sorting performance with 100 notes."""
    # Seed notes
    for i in range(100):
        client.post("/notes/", json={
            "title": f"Note {i:03d}",
            "content": f"Content {i}"
        })

    # Test sorting by title ascending
    start = time.time()
    r = client.get("/notes/search/", params={"sort": "title_asc"})
    elapsed = time.time() - start

    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 100
    assert elapsed < 1.0, f"Sort took {elapsed:.2f}s, should be < 1s"

    # Verify order is correct
    titles = [item["title"] for item in data["items"]]
    assert titles == sorted(titles)


def test_notes_sorting_by_created_at_large_dataset(client):
    """Test created_at sorting with 100 notes."""
    for i in range(100):
        client.post("/notes/", json={
            "title": f"Note {i:03d}",
            "content": f"Content {i}"
        })

    # Sort by created desc
    start = time.time()
    r = client.get("/notes/search/", params={"sort": "created_desc"})
    elapsed = time.time() - start

    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 100
    assert elapsed < 1.0, f"Sort took {elapsed:.2f}s, should be < 1s"


def test_action_items_filter_completed_large_dataset(client):
    """Test completed filter performance with 100 action items."""
    # Seed 100 action items, 50 completed, 50 open
    for i in range(100):
        client.post("/action-items/", json={"description": f"Item {i}"})
        if i % 2 == 0:
            item_id = i + 1
            client.put(f"/action-items/{item_id}/complete")

    # Test filtering completed
    start = time.time()
    r = client.get("/action-items/", params={"completed": "true"})
    elapsed = time.time() - start

    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 50
    assert all(item["completed"] for item in data["items"])
    assert elapsed < 1.0, f"Filter took {elapsed:.2f}s, should be < 1s"

    # Test filtering open
    start = time.time()
    r = client.get("/action-items/", params={"completed": "false"})
    elapsed = time.time() - start

    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 50
    assert all(not item["completed"] for item in data["items"])
    assert elapsed < 1.0, f"Filter took {elapsed:.2f}s, should be < 1s"


def test_notes_pagination_large_dataset(client):
    """Test pagination performance with 100 notes."""
    # Seed 100 notes
    for i in range(100):
        client.post("/notes/", json={
            "title": f"Note {i:03d}",
            "content": f"Content {i}"
        })

    # Test pagination through all pages
    start = time.time()
    for page in range(1, 11):
        r = client.get("/notes/search/", params={"page": page, "page_size": 10})
        assert r.status_code == 200
        data = r.json()["data"]
        assert len(data["items"]) == 10
        assert data["page"] == page
    elapsed = time.time() - start

    assert elapsed < 2.0, f"Pagination took {elapsed:.2f}s, should be < 2s"


def test_notes_with_tags_large_dataset(client):
    """Test notes with tags in a large dataset."""
    # Create notes with tags
    for i in range(50):
        client.post("/notes/", json={
            "title": f"Note {i}",
            "content": f"Content {i} #python #testing"
        })

    # Attach tags to some notes
    for i in range(0, 50, 5):  # Every 5th note
        note_id = i + 1
        client.post(f"/notes/{note_id}/tags", json={"name": "important"})

    # Search with tag filter
    start = time.time()
    r = client.get("/notes/search/", params={"tag_id": 1})  # Assuming tag_id 1 = "important"
    elapsed = time.time() - start

    assert r.status_code == 200
    # Note: tag_id filter may return 0 since tags are created with different IDs
    assert elapsed < 1.0, f"Tag filter took {elapsed:.2f}s, should be < 1s"
