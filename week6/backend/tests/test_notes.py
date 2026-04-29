from pathlib import Path

from backend.app.routers import notes


def _remove_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def test_create_list_and_patch_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    note_id = data["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"


def test_debug_eval_allows_arithmetic(client):
    r = client.get("/notes/debug/eval", params={"expr": "1 + 2 * 3"})

    assert r.status_code == 200
    assert r.json() == {"result": "7"}


def test_debug_eval_rejects_code_execution(client):
    r = client.get(
        "/notes/debug/eval",
        params={"expr": '__import__("os").system("whoami")'},
    )

    assert r.status_code == 400


def test_debug_run_allows_known_command(client):
    r = client.get("/notes/debug/run", params={"cmd": "python-version"})

    assert r.status_code == 200
    data = r.json()
    assert data["returncode"] == "0"
    assert "Python" in data["stdout"] or "Python" in data["stderr"]


def test_debug_run_rejects_shell_injection(client):
    r = client.get("/notes/debug/run", params={"cmd": "python-version; whoami"})

    assert r.status_code == 400
    assert r.json()["detail"] == "Command not allowed"


def test_unsafe_search_treats_sql_payload_as_plain_text(client):
    client.post("/notes/", json={"title": "needle", "content": "safe content"})
    client.post("/notes/", json={"title": "unrelated", "content": "ordinary content"})

    r = client.get("/notes/unsafe-search", params={"q": "' OR 1=1 --"})

    assert r.status_code == 200
    assert r.json() == []


def test_debug_read_allows_file_inside_base_dir(client, monkeypatch):
    base_dir = Path("data/debug_read_base")
    base_dir.mkdir(exist_ok=True)
    readable_file = base_dir / "readme.txt"
    readable_file.write_text("safe file content", encoding="utf-8")
    monkeypatch.setattr(notes, "_READ_BASE_DIR", base_dir.resolve())

    try:
        r = client.get("/notes/debug/read", params={"path": "readme.txt"})
    finally:
        _remove_if_exists(readable_file)

    assert r.status_code == 200
    assert r.json() == {"snippet": "safe file content"}


def test_debug_read_rejects_path_traversal(client, monkeypatch):
    base_dir = Path("data/debug_read_base")
    base_dir.mkdir(exist_ok=True)
    secret_file = Path("data/debug_read_secret.txt")
    secret_file.write_text("do not leak", encoding="utf-8")
    monkeypatch.setattr(notes, "_READ_BASE_DIR", base_dir.resolve())

    try:
        r = client.get("/notes/debug/read", params={"path": "../debug_read_secret.txt"})
    finally:
        _remove_if_exists(secret_file)

    assert r.status_code == 400
    assert r.json()["detail"] == "Invalid path"


def test_debug_read_rejects_absolute_path_escape(client, monkeypatch):
    base_dir = Path("data/debug_read_base")
    base_dir.mkdir(exist_ok=True)
    secret_file = Path("data/debug_read_secret.txt")
    secret_file.write_text("do not leak", encoding="utf-8")
    monkeypatch.setattr(notes, "_READ_BASE_DIR", base_dir.resolve())

    try:
        r = client.get("/notes/debug/read", params={"path": str(secret_file.resolve())})
    finally:
        _remove_if_exists(secret_file)

    assert r.status_code == 400
    assert r.json()["detail"] == "Invalid path"
