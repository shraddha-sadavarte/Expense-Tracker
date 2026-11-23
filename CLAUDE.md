# CLAUDE.md — standing rules for this repository

The source of truth for architecture, database, APIs, security and testing is
`docs/BLUEPRINT.md`. If an instruction conflicts with it, stop and ask the owner.

## Non-negotiable rules

- **Money is ALWAYS integer paise** (`BIGINT` in Postgres, `int` in Python, `int`
  in Dart). Never `float` or `double` for money anywhere. There is exactly one
  audited money module per codebase:
  - backend: `backend/app/core/money.py`
  - mobile: `mobile/lib/core/money/`
- **`user_id` comes only from the verified JWT**, never from the client or an
  LLM. Every repository query takes `user_id`. Objects owned by another user
  return `404 NOT_FOUND` (existence is never leaked).
- **Layering** (BLUEPRINT Doc 9.7): business rules live in `service.py`;
  `router.py` does HTTP only; `repository.py` does queries only; `models.py`
  mirrors Doc 3. Services call other modules only through their services.
  Nothing imports a router. `analytics` never imports write paths. These are
  enforced by import-linter (`lint-imports`).
- **LLMs never calculate or write data.** Do not invent provider capabilities
  (UPI apps, Account Aggregator). Anything unverified is marked `TODO-VERIFY`.
- **Write tests with the code.** Money, budget, state-machine and database
  constraint code is not done until it has tests.
- **Small commits**, one concern each, with clear messages. Run lint, type
  check and tests before every commit.
- **Never commit secrets.** Use `.env.example` with placeholders; real values
  live in `.env` (git-ignored).
- **When a decision is missing from the blueprint, ask the owner; do not guess.**

## Conventions

- API base path `/api/v1`; `/health` and `/ready` live at the root.
- Error shape (Doc 5.1):
  `{"error": {"code": "...", "message": "...", "details": {...}, "request_id": "..."}}`.
  Request validation failures are `400 VALIDATION_ERROR`.
- Timestamps are UTC `TIMESTAMPTZ`; day logic uses the user's timezone
  (default `Asia/Kolkata`).
- Backend: Python 3.12, FastAPI, SQLAlchemy 2 (async, psycopg 3), Alembic,
  Pydantic v2, Celery + Redis. Dependencies are pinned in `backend/uv.lock`.
- Mobile: Flutter, Material 3, Riverpod, go_router, Dio. Feature-first folders
  (Doc 9.6): `features/<name>/{data,domain,presentation}`.

## Day-to-day commands

Run from the repo root. `make` works in Git Bash / CI; on PowerShell use
`./infra/dev.ps1 <target>` with the same target names.

| Command | What it does |
| --- | --- |
| `make up` | Start postgres, redis, api, worker, beat (Docker Compose) |
| `make down` | Stop everything |
| `make test` | Backend tests (needs `make up` for the DB tests) |
| `make lint` | ruff, ruff format check, mypy, import-linter |
| `make migrate` | Apply Alembic migrations |
| `make revision m="message"` | Create a new Alembic revision |
| `cd mobile && flutter test` | Mobile tests |
