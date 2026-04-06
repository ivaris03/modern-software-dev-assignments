import re


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


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
