from backend.app.services.extract import extract_action_items, extract_tags


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


def test_extract_tags():
    text = "This is a note with #tag and #another_tag and #tag3"
    tags = extract_tags(text)
    assert "#tag" in tags
    assert "#another_tag" in tags
    assert "#tag3" in tags
    assert len(tags) == 3


def test_extract_tags_empty():
    text = "This is a note without any tags"
    tags = extract_tags(text)
    assert tags == []


def test_extract_tags_standalone():
    text = "#onlytag"
    tags = extract_tags(text)
    assert tags == ["#onlytag"]
