# MehnatLedger

A voice-first recordkeeping app for Indian shopkeepers, small-business owners and
daily-wage workers: a simple digital hisaab notebook with Business Mode, Worker
Mode and an opt-in Shared Hisaab workflow.

**MehnatLedger is not** a court, a legal authority, a full accounting or payroll
system, a bank, or proof that a debt exists.

## Project status — read this first

This repository is being built in phases (`phases.md`). It currently contains
**Phase 1: project foundation and design shell only**.

| Area | State |
| --- | --- |
| Specification documents (`prd.md`, `architecture.md`, `rules.md`, `phases.md`, `design.md`, `memory.md`) | Complete |
| Backend app, typed configuration, health + capability endpoints | Implemented and tested |
| Frontend app shell, design tokens, navigation, mode selection, empty states | Implemented; build and typecheck pass |
| Token verification, ownership-scoped profile, `/api/v1/me` (Phase 2) | Implemented; 50 backend tests pass. **Verified only with locally minted tokens — the live Supabase handshake is untested.** |
| Sign-in UI / obtaining a token (Phase 2) | Not started |
| Supabase project connection | Not configured — `ML_SUPABASE_URL` is unset, so `/api/v1/me` currently returns 503 |
| Business and worker ledgers, balances (Phase 3) | Not started |
| Shared Hisaab and disputes (Phase 4) | Not started |
| Voice entry and AI providers (Phase 5) | Not started |
| Gnani speech integration | **Not integrated.** The owner has access and will supply credentials via `backend/.env`, but no request has ever been made and no endpoint, quota or language list has been verified. |
| Reasoning / extraction provider | **Not selected.** No provider has been approved. |
| Supabase (Auth + PostgreSQL) | **Chosen by the owner (2026-10-27), not yet implemented or connected.** No Supabase project exists for this repo yet. |
| PostgreSQL | Chosen production target is Supabase Postgres. No database is in use yet; local development uses SQLite because no PostgreSQL server is available here. |

Screens that correspond to unbuilt features say so in plain language and
**do not save anything**. The application is never seeded with invented sample
businesses, workers, wages or transactions.

## Requirements

- **Python 3.12+** and [`uv`](https://docs.astral.sh/uv/)
- **Node.js 20+** and npm
- No PostgreSQL server is required for local development (see *Database* below)

The versions used to verify this phase were Python 3.14.3, uv 0.10.9,
Node v24.20.0 and npm 11.19.0.

## Setup

### 1. Backend

```bash
cd backend
cp .env.example .env      # optional: the defaults already work for local dev
uv sync
uv run alembic upgrade head   # create the schema
uv run uvicorn app.main:app --reload --port 8000
```

Check it is running:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/system/capabilities
```

Interactive API docs (development only) are at <http://127.0.0.1:8000/docs>.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://127.0.0.1:5173>. The Vite dev server proxies `/api` to
`http://127.0.0.1:8000`, so the browser makes same-origin requests in
development.

The first visit asks you to choose **Business** or **Worker** mode. That choice
is currently stored on the device only, because accounts do not exist yet.

## Commands

| Where | Command | What it does |
| --- | --- | --- |
| `backend/` | `uv run pytest` | Run backend tests |
| `backend/` | `uv run ruff check .` | Lint the backend |
| `backend/` | `uv run ruff format --check .` | Check formatting |
| `backend/` | `uv run alembic upgrade head` | Apply database migrations |
| `backend/` | `uv run alembic revision --autogenerate -m "..."` | Create a migration from the models |
| `backend/` | `uv run alembic downgrade base` | Revert all migrations |
| `frontend/` | `npm run typecheck` | Type-check with `tsc` |
| `frontend/` | `npm run build` | Type-check and produce `dist/` |
| `frontend/` | `npm run dev` | Start the dev server on port 5173 |

## Configuration and secrets

- All secret values live in `backend/.env`, which is **git-ignored**. Start from
  `backend/.env.example`, which contains placeholders only.
- Nothing secret may be placed in the frontend. Every `VITE_`-prefixed variable
  is embedded in the browser bundle and is public; see `frontend/.env.example`.
- Provider credentials are read on the server only. The API exposes only
  booleans about whether a credential is present, never a value or a base URL.
- Never paste a real key into chat, a commit, a log or a screenshot.

### Running in production configuration

The settings module refuses to start with unsafe production values:
`ML_ENVIRONMENT=production` requires a real PostgreSQL connection string and
explicit (non-wildcard) CORS origins. Interactive docs are disabled in
production.

## Database

Supabase PostgreSQL is the chosen production target. For local development the
default is a throwaway SQLite file (`backend/mehnatledger_dev.db`, git-ignored)
because no PostgreSQL server is available in this environment.

To point the backend at Supabase PostgreSQL, copy the connection string from
Supabase **Dashboard → Connect** and change its scheme to `postgresql+psycopg://`:

```bash
export ML_DATABASE_URL="postgresql+psycopg://postgres:PASSWORD@db.PROJECTREF.supabase.co:5432/postgres"
```

Use the **direct** connection string for a stationary server (a VM or
long-running container). Supabase's documentation notes that the direct
connection resolves to an IPv6 address and will not work on an IPv4-only
network; in that case use the Supavisor pooler in **session** mode (port 5432).
Do not use transaction mode (port 6543) for migrations.

Do not commit a real connection string: it contains a password.

**Limitation:** because PostgreSQL is not installed here, nothing in this
repository has been verified against PostgreSQL yet. Tests run against SQLite.

## Repository layout

```text
backend/
  app/
    api/v1/        # versioned HTTP routers (system endpoints so far)
    core/          # typed settings and logging
    schemas/       # Pydantic request/response schemas
  tests/           # pytest suite
  .env.example
frontend/
  src/
    app/           # shell, navigation, page header, planned-feature labels
    components/ui/ # small shared components
    features/      # mode state, capability checks, voice action
    pages/         # one file per screen
    services/api/  # typed API client
  .env.example
```

## Environment notes

- This checkout is inside a OneDrive-synced folder. File sync can interfere with
  `node_modules` and with long-running processes; consider excluding the project
  folder from sync if you hit odd file-locking errors.
- There is no `gh` CLI on this machine, so remote setup is done with plain `git`.

## Migrations

The database URL is read from `ML_DATABASE_URL` inside `alembic/env.py`; no
connection string is stored in `alembic.ini`, because a real one contains a
password. Tests override the URL programmatically so they run against an
isolated temporary database built by the real migrations.

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "describe the change"
```

`alembic/env.py` enables SQLite batch mode, because SQLite cannot `ALTER` most
column definitions. The same migrations therefore run in local development and
on PostgreSQL.

## Authentication

Supabase Auth was chosen by the owner on 2026-10-27 (see `memory.md`). Token
verification is implemented; a sign-in UI is not. The approach, based on
Supabase's current official documentation:

| Endpoint | Behaviour without a configured project |
| --- | --- |
| `GET /api/v1/health` | 200 |
| `GET /api/v1/system/capabilities` | 200 (no credential values) |
| `GET /api/v1/me` | **503** — reports a setup requirement, not a bad credential |
| `GET /api/v1/me` with a bearer token, once configured | 200 for a valid token; 401 for missing, expired or forged tokens |


- Verify user access tokens against the project's public **JWKS** endpoint
  (`{ML_SUPABASE_URL}/auth/v1/.well-known/jwks.json`) using asymmetric signing
  keys. Supabase documents this as the recommended approach: verification is
  local, key rotation is automatic, and rotation does not sign users out.
- The **legacy shared JWT secret** is supported for backward compatibility but is
  no longer recommended. If a project still uses it, rotation will break any
  component verifying with the shared secret.
- The frontend must never receive a service-role key. Privileged database
  credentials stay server-side.
- **The `aud` claim is not enforced by default.** Supabase's JWT payload
  reference does not list one, so enforcing a guessed value would reject every
  genuine token. Read the value from a real access token, then set
  `ML_SUPABASE_JWT_AUDIENCE`.
- **A public key never verifies an HS256 token.** Only asymmetric algorithms are
  accepted on the JWKS path, which closes the algorithm-confusion attack where an
  attacker signs an HMAC token using the public key as the secret.
- The application creates its own `profiles` row lazily on first authenticated
  request. It never writes to Supabase's `auth.users`.

**Limitation:** token verification is covered by 17 tests (of 50 backend tests
total), but they mint tokens locally and supply an in-process JWKS. Only the
network fetch is stubbed, so signature, expiry and issuer handling are genuinely
tested — while the live Supabase handshake is **not** verified and must not be
described as working.

## Next phase

Finish `phases.md` **Phase 2** by connecting a real Supabase project and
verifying the live handshake, then add the sign-in UI so a user can obtain a
token. Phase 3 (core individual ledgers) follows. See `memory.md` section 9 for
the current handoff state.
