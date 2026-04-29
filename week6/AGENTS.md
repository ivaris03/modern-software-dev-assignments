# AGENTS.md

Guidance for coding agents working in `week6/`.

## Verification

Run tests from `week6/` with:

```powershell
conda run -n cs146s python -m pytest -q backend\tests
```

On this Windows machine, `make test` and `make run` fail before pytest/uvicorn starts.
