import re


def extract_action_items(text: str) -> list[str]:
    """Extract action items from text.

    Recognizes:
    - GitHub-style task list items: - [ ] task text
    - Lines ending with !
    - Lines starting with TODO:
    """
    items = []
    for line in text.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue
        # Check for GitHub-style task list: - [ ] task text
        if line_stripped.startswith("- [ ] "):
            task_text = line_stripped[6:].strip()
            if task_text:
                items.append(task_text)
        # Check for legacy formats (ending with ! or starting with TODO:)
        # Strip leading "- " prefix for the check and extraction
        else:
            stripped = line_stripped.strip("- ")
            if stripped.endswith("!") or stripped.lower().startswith("todo:"):
                items.append(stripped)
    return items


def extract_hashtags(text: str) -> list[str]:
    """Extract #hashtags from text, returning unique tag names without the # symbol."""
    hashtags = re.findall(r"#(\w+)", text)
    # Return unique tags, preserving order of first appearance
    seen = set()
    unique = []
    for tag in hashtags:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            unique.append(tag)
    return unique
