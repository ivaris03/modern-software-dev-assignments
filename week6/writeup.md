# Week 6 Write-up

## Submission Details

Name: **TODO**
SUNet ID: **TODO**
Citations: Semgrep CLI output from `semgrep ci --subdir week6`; Semgrep rule detail links shown in the scan output.

This assignment took me about **TODO** hours to do.

## Brief Findings Overview

Semgrep reported both code findings and supply-chain findings.

The code findings included unsafe dynamic evaluation, unsafe shell command execution, SQL injection risk, arbitrary file reads/path traversal, dynamic URL fetching, and wildcard CORS. The supply-chain findings came from outdated pinned dependencies in `requirements.txt`, including old versions of Werkzeug, requests, Jinja2, PyYAML, and pydantic.

I prioritized direct application-code vulnerabilities because they are reachable from FastAPI request parameters and have clear, targeted fixes. I treated the `stmt.offset(skip).limit(limit)` findings as noisy/lower risk because FastAPI parses those values as integers and SQLAlchemy builds the query rather than interpolating raw SQL strings. I also upgraded the vulnerable pinned dependencies in `requirements.txt` and ran the backend test suite to check compatibility.

## Fix 1: Replace `eval` With Safe Arithmetic Parsing

File and lines: `backend/app/routers/notes.py`, around `debug_eval`.

Semgrep category:

- `python.fastapi.code.tainted-code-stdlib-fastapi.tainted-code-stdlib-fastapi`
- `python.lang.security.audit.eval-detected.eval-detected`

Risk: The endpoint accepted `expr` from the query string and evaluated it with Python `eval`. A malicious request could execute Python code on the server instead of only evaluating a simple expression.

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

Mitigation: I used Codex to replace `eval` with an AST-based arithmetic evaluator. The helper only allows numeric constants and specific arithmetic operators. Function calls, imports, names, attributes, and other code-like syntax are rejected before anything can execute.

Regression tests:

- `test_debug_eval_allows_arithmetic`
- `test_debug_eval_rejects_code_execution`

## Fix 2: Replace Shell Execution With a Command Allowlist

File and lines: `backend/app/routers/notes.py`, around `debug_run`.

Semgrep category:

- `python.fastapi.os.tainted-os-command-stdlib-fastapi-secure-default.tainted-os-command-stdlib-fastapi-secure-default`
- `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true`

Risk: The endpoint accepted `cmd` from the query string and passed it to `subprocess.run(..., shell=True)`. Because the string was interpreted by a shell, an attacker could use shell syntax such as `;`, `&`, or `|` to run additional commands.

Before:

```python
@router.get("/debug/run")
def debug_run(cmd: str) -> dict[str, str]:
    import subprocess

    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
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

Mitigation: The user now controls only a symbolic command name. The server maps that name to a fixed argument list and runs it without `shell=True`, so shell metacharacters in user input are not interpreted as executable syntax.

Regression tests:

- `test_debug_run_allows_known_command`
- `test_debug_run_rejects_shell_injection`

## Fix 3: Replace SQL String Interpolation With SQLAlchemy ORM

File and lines: `backend/app/routers/notes.py`, around `unsafe_search`.

Semgrep category:

- `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text`
- `python.fastapi.db.sqlalchemy-fastapi.sqlalchemy-fastapi`
- `python.fastapi.db.generic-sql-fastapi.generic-sql-fastapi`

Risk: The endpoint inserted the request parameter `q` directly into a SQL string with an f-string. An attacker could provide input such as `' OR 1=1 --` to alter the SQL query logic.

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

Mitigation: SQLAlchemy now builds the SQL statement and treats the user-controlled search text as data. Injection payloads are interpreted as literal search strings instead of SQL syntax.

Regression test:

- `test_unsafe_search_treats_sql_payload_as_plain_text`

## Fix 4: Restrict Debug File Reads to a Safe Directory

File and lines: `backend/app/routers/notes.py`, around `debug_read`.

Semgrep category:

- `python.fastapi.file.tainted-path-traversal-stdlib-fastapi.tainted-path-traversal-stdlib-fastapi`

Risk: The endpoint accepted `path` from the query string and passed it directly to `open(path)`. A malicious user could request paths such as `../...` or an absolute path to read files outside the intended application data area.

Before:

```python
@router.get("/debug/read")
def debug_read(path: str) -> dict[str, str]:
    try:
        content = open(path).read(1024)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from None
    return {"snippet": content}
```

After:

```python
_READ_BASE_DIR = Path("data").resolve()


@router.get("/debug/read")
def debug_read(path: str) -> dict[str, str]:
    requested_path = (_READ_BASE_DIR / path).resolve()
    if not requested_path.is_relative_to(_READ_BASE_DIR):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not requested_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        content = requested_path.read_text(encoding="utf-8")[:1024]
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    return {"snippet": content}
```

Mitigation: The endpoint now resolves the requested path against a fixed base directory and confirms the final path is still inside that base directory. This blocks both `../` traversal and absolute-path escapes. It also checks that the target is a file before reading it.

Regression tests:

- `test_debug_read_allows_file_inside_base_dir`
- `test_debug_read_rejects_path_traversal`
- `test_debug_read_rejects_absolute_path_escape`

## Fix 5: Upgrade Vulnerable Pinned Dependencies

File: `requirements.txt`.

Semgrep category:

- Reachable and undetermined supply-chain findings for old versions of `Werkzeug`, `requests`, `Jinja2`, `PyYAML`, and `pydantic`

Risk: The original dependency pins were several years old and matched multiple published CVEs. The highest-priority Semgrep supply-chain result was a reachable high-severity Werkzeug finding. Other outdated packages included `requests`, `PyYAML`, `Jinja2`, and `pydantic`.

Before:

```text
fastapi==0.65.2
uvicorn==0.11.8
sqlalchemy==1.3.23
pydantic==1.5.1
requests==2.19.1
PyYAML==5.1
Jinja2==2.10.1
MarkupSafe==1.1.0
Werkzeug==0.14.1
```

After:

```text
fastapi==0.116.1
uvicorn[standard]==0.35.0
sqlalchemy==2.0.43
pydantic==2.11.7
requests==2.33.0
PyYAML==6.0.2
Jinja2==3.1.6
MarkupSafe==3.0.2
Werkzeug==3.1.6
python-dotenv==1.1.1
```

Mitigation: I updated the pinned dependencies to modern versions that satisfy the fixed-version guidance from the Semgrep output. I kept the versions aligned with the current code style, which already uses SQLAlchemy 2 and Pydantic 2 APIs such as `model_validate` and `from_attributes`. I also added `python-dotenv` because `backend/app/db.py` imports `load_dotenv`, so a fresh install needs that dependency declared explicitly.

## Fix 6: Replace Wildcard CORS With Explicit Local Origins

File and lines: `backend/app/main.py`, around the `CORSMiddleware` configuration.

Semgrep category:

- `python.fastapi.security.wildcard-cors.wildcard-cors`

Risk: The application configured CORS with `allow_origins=["*"]` while also allowing credentials. A wildcard CORS policy lets any website make cross-origin browser requests to the API. In a production setting, that can expose authenticated endpoints or private API behavior to untrusted origins.

Before:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

After:

```python
ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Mitigation: I replaced the wildcard with an explicit allowlist for the local development origins used by the Week 6 app. This keeps the browser-based frontend working locally while preventing arbitrary external origins from receiving cross-origin access.

## Verification

I installed the updated `requirements.txt` and ran the project tests from `week6/`. After the CORS fix, I also reran the tests:

```powershell
python -m pytest -q
```

Result:

```text
11 passed
```

I also checked `make test`. On this Windows machine, it failed before pytest started because Git Bash could not create a signal pipe, so I used the PowerShell pytest command above for verification.

I did not rerun `semgrep ci --subdir week6` after the dependency upgrade because that command uploads scan results to Semgrep Cloud. The local dependency pins have been updated, and the backend tests pass.
