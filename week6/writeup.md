# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do.


## Brief findings overview
Semgrep reported both code and supply-chain findings. The code findings included
an unsafe debug endpoint that evaluated user-controlled input with `eval`, an
unsafe shell command endpoint, unsafe SQL string construction, dynamic URL/file
access, and wildcard CORS. The supply-chain findings came from outdated pinned
dependencies in `requirements.txt`, including old versions of Werkzeug,
requests, Jinja2, PyYAML, and pydantic.

For these fixes, I prioritized the `eval(expr)` finding and the `shell=True`
subprocess finding because both can allow direct code or command execution from
request parameters. I treated some other findings, such as
`offset(skip).limit(limit)`, as lower priority/noisier because FastAPI parses
those values as integers and SQLAlchemy builds the query rather than interpolating
raw SQL strings.

## Fix #1
a. File and line(s)
`backend/app/routers/notes.py`, previously line 104:

```python
result = str(eval(expr))  # noqa: S307
```

b. Rule/category Semgrep flagged
Code injection / unsafe dynamic evaluation:

- `python.fastapi.code.tainted-code-stdlib-fastapi.tainted-code-stdlib-fastapi`
- `python.lang.security.audit.eval-detected.eval-detected`

c. Brief risk description
The endpoint accepted `expr` from the request query string and passed it directly
to Python `eval`. That means a request such as
`/notes/debug/eval?expr=__import__("os").system("whoami")` could execute Python
code or operating system commands on the server.

d. Your change (short code diff or explanation, AI coding tool usage)
I used Codex to replace direct `eval` with a small allowlisted arithmetic
evaluator based on Python's `ast` module. The endpoint still supports the intended
debug calculator behavior, such as `1 + 2 * 3`, but rejects function calls,
imports, attribute access, names, and other code-like syntax.

Before:

```python
@router.get("/debug/eval")
def debug_eval(expr: str) -> dict[str, str]:
    result = str(eval(expr))  # noqa: S307
    return {"result": result}
```

After:

```python
@router.get("/debug/eval")
def debug_eval(expr: str) -> dict[str, str]:
    try:
        result = str(_safe_calculate(expr))
    except (ArithmeticError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    return {"result": result}
```

I also added tests in `backend/tests/test_notes.py` to confirm that arithmetic is
accepted and a code execution payload is rejected. While running the tests on
Windows, I fixed the test fixture in `backend/tests/conftest.py` by disposing the
SQLAlchemy engine before deleting the temporary SQLite file.

e. Why this mitigates the issue
The new implementation parses the input into an AST and recursively evaluates
only explicitly allowed numeric nodes and operators. Anything outside that
allowlist raises an error before it can execute. Because the code no longer
passes user input to `eval`, user-controlled strings are treated as data instead
of executable Python code.

Verification:

```powershell
conda run -n cs146s python -m pytest -q backend\tests
```

Result: `8 passed`.

## Fix #2
a. File and line(s)
`backend/app/routers/notes.py`, previously line 163:

```python
completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # noqa: S602,S603
```

b. Rule/category Semgrep flagged
Command injection / unsafe shell execution:

- `python.fastapi.os.tainted-os-command-stdlib-fastapi-secure-default.tainted-os-command-stdlib-fastapi-secure-default`
- `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true`

c. Brief risk description
The endpoint accepted `cmd` from the request query string and passed it directly
to `subprocess.run` with `shell=True`. Because the command string was interpreted
by the operating system shell, an attacker could include shell syntax such as
`;`, `&`, or `|` to run additional commands. For example, an input like
`python --version; whoami` could execute both commands instead of being treated
as a single safe argument.

d. Your change (short code diff or explanation, AI coding tool usage)
I used Codex to replace arbitrary shell command execution with a small allowlist
of supported debug commands. The endpoint now accepts only the symbolic command
name `python-version`, maps it to a fixed argument list, and runs it without
`shell=True`.

Before:

```python
@router.get("/debug/run")
def debug_run(cmd: str) -> dict[str, str]:
    import subprocess

    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # noqa: S602,S603
    return {
        "returncode": str(completed.returncode),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
```

After:

```python
@router.get("/debug/run")
def debug_run(cmd: str) -> dict[str, str]:
    import subprocess
    import sys

    allowed_commands = {
        "python-version": [sys.executable, "--version"],
    }
    if cmd not in allowed_commands:
        raise HTTPException(status_code=400, detail="Command not allowed")

    completed = subprocess.run(
        allowed_commands[cmd],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return {
        "returncode": str(completed.returncode),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
```

I also added tests in `backend/tests/test_notes.py` to confirm that
`cmd=python-version` succeeds and an injection-style value such as
`cmd=python-version; whoami` is rejected.

e. Why this mitigates the issue
The new code no longer gives user input to a shell. The user controls only a
small command name, and the server translates that name into a fixed list of
arguments. Since `subprocess.run` receives a list and `shell=True` is not used,
shell metacharacters in user input are not interpreted as executable syntax. The
allowlist also prevents callers from choosing arbitrary programs to run.

Verification:

```powershell
conda run -n cs146s python -m pytest -q backend\tests
```

Result: `8 passed`.

## Fix #3
a. File and line(s)
`backend/app/routers/notes.py`, previously lines 71-80:

```python
sql = text(
    f"""
    SELECT id, title, content, created_at, updated_at
    FROM notes
    WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
    ORDER BY created_at DESC
    LIMIT 50
    """
)
rows = db.execute(sql).all()
```

b. Rule/category Semgrep flagged
SQL injection / unsafe SQL construction:

- `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text`
- `python.fastapi.db.sqlalchemy-fastapi.sqlalchemy-fastapi`
- `python.fastapi.db.generic-sql-fastapi.generic-sql-fastapi`

c. Brief risk description
The endpoint accepted the search query `q` from the request and inserted it
directly into a SQL string with an f-string. Because the user-controlled value
became part of the SQL syntax, an attacker could provide input such as
`' OR 1=1 --` to change the `WHERE` clause and return rows that should not match
the search. In a more permissive database configuration, this pattern can also
lead to data modification or deletion attempts.

d. Your change (short code diff or explanation, AI coding tool usage)
I used Codex to replace the hand-written SQL string with a SQLAlchemy ORM query.
The endpoint keeps the same route and response shape, but the search term is now
handled as data by SQLAlchemy instead of being interpolated into raw SQL. I also
moved the fixed `/notes/unsafe-search` route before `/notes/{note_id}` so FastAPI
matches the literal route before the dynamic note-id route.

Before:

```python
@router.get("/unsafe-search", response_model=list[NoteRead])
def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    sql = text(
        f"""
        SELECT id, title, content, created_at, updated_at
        FROM notes
        WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
        ORDER BY created_at DESC
        LIMIT 50
        """
    )
    rows = db.execute(sql).all()
    ...
```

After:

```python
@router.get("/unsafe-search", response_model=list[NoteRead])
def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    stmt = (
        select(Note)
        .where((Note.title.contains(q)) | (Note.content.contains(q)))
        .order_by(desc(Note.created_at))
        .limit(50)
    )
    rows = db.execute(stmt).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]
```

I also removed the now-unused `text` import from `backend/app/routers/notes.py`
and added a regression test in `backend/tests/test_notes.py`:

```python
def test_unsafe_search_treats_sql_payload_as_plain_text(client):
    client.post("/notes/", json={"title": "needle", "content": "safe content"})
    client.post("/notes/", json={"title": "unrelated", "content": "ordinary content"})

    r = client.get("/notes/unsafe-search", params={"q": "' OR 1=1 --"})

    assert r.status_code == 200
    assert r.json() == []
```

e. Why this mitigates the issue
The new query is built with SQLAlchemy expressions, so the SQL structure is
fixed by the application code and the request parameter is treated as a value.
Attack strings like `' OR 1=1 --` are interpreted as literal search text instead
of SQL syntax. This removes the injection path while preserving the intended
title/content search behavior.

Verification:

```powershell
conda run -n cs146s python -m pytest -q backend\tests
```

Result: `8 passed`.
