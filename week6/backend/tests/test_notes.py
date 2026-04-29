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
