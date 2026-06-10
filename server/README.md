# DynoDoc — Server

FastAPI backend for DynoDoc. Package management with **uv**. Architecture and conventions
are documented in [`../docs/version_1/`](../docs/version_1/).

## Prerequisites
- Python 3.13
- [uv](https://docs.astral.sh/uv/)

## Setup
```bash
uv sync                     # create .venv and install runtime + dev deps
cp .env.example .env        # optional; sane defaults exist
```

## Run
```bash
uv run uvicorn app.runtime.application:app --reload
# → http://127.0.0.1:8000/health   ·   docs at /docs
```

## Quality gates (same as CI / pre-commit)
```bash
uv run ruff check .         # lint (+ import order)
uv run ruff format .        # format
uv run mypy app             # strict type check
uv run pytest               # tests
uv run pytest --cov         # tests + coverage
```

## Layout
```
app/
  domains/      business logic, one folder per bounded context
  entrypoints/  http / mcp / workers  (driving adapters)
  platform/     auth, database, cache, llm, vectorstore, sandbox, ... (driven adapters)
  processes/    cross-domain orchestration / workflows
  runtime/      settings, bootstrap (DI), application, lifespan, request_context
  shared/       contracts (ports), errors, events, common types
tests/          unit · contracts · integration · processes · e2e · evals
```
See `docs/version_1/02-architecture.md` for the dependency rules.
