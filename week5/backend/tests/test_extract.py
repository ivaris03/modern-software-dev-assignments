from backend.app.services.extract import extract_action_items, extract_hashtags


def test_extract_action_items_github_style():
    """Test extraction of GitHub-style task list items."""
    text = """
    This is a note with tasks:
    - [ ] Write tests
    - [ ] Review code
    - [ ] Deploy
    """.strip()
    items = extract_action_items(text)
    assert "Write tests" in items
    assert "Review code" in items
    assert "Deploy" in items


def test_extract_action_items_legacy_formats():
    """Test extraction of legacy action item formats (ending with ! or starting with TODO:)."""
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    # The original code stripped "- " prefix first, so "- TODO: write tests" became "TODO: write tests"
    assert "TODO: write tests" in items
    # But "- Ship it!" would become "Ship it!" after stripping "- " (since it doesn't start with "TODO:")
    assert "Ship it!" in items


def test_extract_action_items_mixed():
    """Test extraction with mixed action item formats."""
    text = """
    - [ ] First task
    - [ ] Second task
    Important item!
    TODO: fix bug
    """.strip()
    items = extract_action_items(text)
    assert "First task" in items
    assert "Second task" in items
    assert "Important item!" in items
    assert "TODO: fix bug" in items


def test_extract_action_items_empty():
    """Test extraction with no action items."""
    text = "This is just a regular note without any tasks."
    items = extract_action_items(text)
    assert items == []


def test_extract_hashtags():
    """Test hashtag extraction."""
    text = "This note has #python and #testing tags"
    tags = extract_hashtags(text)
    assert "python" in tags
    assert "testing" in tags


def test_extract_hashtags_unique():
    """Test that duplicate hashtags are returned only once (case-insensitive)."""
    text = "#Python #python #PYTHON #python3"
    tags = extract_hashtags(text)
    # Should have 2 unique tags (case-insensitive deduplication, preserving first-seen case)
    assert len(tags) == 2
    assert "Python" in tags
    assert "python3" in tags


def test_extract_hashtags_empty():
    """Test extraction with no hashtags."""
    text = "This note has no hashtags"
    tags = extract_hashtags(text)
    assert tags == []
