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

For this fix, I prioritized the `eval(expr)` finding because it allows direct
code execution from a request parameter. I treated some other findings, such as
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

Result: `5 passed`.

## Fix #2
a. File and line(s)
> TODO

b. Rule/category Semgrep flagged
> TODO

c. Brief risk description
> TODO

d. Your change (short code diff or explanation, AI coding tool usage)
> TODO

e. Why this mitigates the issue
> TODO

## Fix #3
a. File and line(s)
> TODO

b. Rule/category Semgrep flagged
> TODO

c. Brief risk description
> TODO

d. Your change (short code diff or explanation, AI coding tool usage)
> TODO

e. Why this mitigates the issue
> TODO
