# MehnatLedger — Project Memory and Session Handoff

**Purpose:** This is a compact persistent memory for the coding agent. Read it before starting work and update it after meaningful changes. Do not treat an item marked *proposed* as a confirmed user decision.

## 1. Product identity

- **Name:** MehnatLedger.
- **Core idea:** A voice-first recordkeeping app with a Business Mode for shopkeepers/small-business owners, a Worker Mode for daily-wage/informal workers, and an opt-in Shared Hisaab workflow for specific work/payment records.
- **Primary product value:** Make it easy to record and review ordinary business and work/payment entries, while making shared records transparent and disputes explicit.
- **Important product boundary:** MehnatLedger is not a judge, legal authority, full accounting/tax system, bank, payroll-compliance system or guaranteed proof of a debt.

## 2. User-confirmed constraints from the project discussion

- The app should serve **shopkeepers/business owners as well as labourers/workers**; the pitch may demonstrate both audiences.
- Gnani voice models are intended for speech-related capabilities, but the owner has limited Gnani credits.
- Reasoning/extraction should be handled separately from Gnani speech models to conserve those credits.
- End users must not have to supply their own provider API keys to use the deployed app.
- The owner's provider secrets must not be exposed in frontend code, browser requests or the GitHub repository.
- The project owner wants the coding agent to be truthful, avoid hallucinations, and ask for help when a material issue genuinely blocks progress.
- Do not purchase services, use unexpected paid APIs or enable billing without explicit approval.

## 3. Proposed technical direction (validate against the existing repository)

- Frontend: React + TypeScript + Vite + Tailwind CSS.
- Backend: Python + FastAPI + Pydantic.
- Database: PostgreSQL; Supabase is a possible managed option.
- Database access/migrations: SQLAlchemy + Alembic are proposed.
- Voice: Gnani Prisma for speech-to-text and Gnani Timbre for text-to-speech, using only verified current official API docs and server-side credentials.
- Reasoning/extraction: separate provider abstraction; local/open-weight inference is preferred for cost control where feasible. Ollama is one option to evaluate, not a confirmed production host or guaranteed free deployed service.
- Deployment: frontend and backend deployed separately, or another arrangement only after its security implications are understood. GitHub stores source, never live secrets.
- Authentication provider, production database host, production reasoning model and final deployment hosts remain unconfirmed.

## 4. Architecture and safety invariants

- User identity and authorization are enforced on the backend, never trusted from the request body alone.
- A business-worker link is opt-in and requires acceptance; linked users only see explicitly shared records.
- A shared record can be proposed, acknowledged or disputed; payment/settlement is a distinct fact. Acknowledgment does not prove legal truth.
- LLM output is untrusted. Validate it, show a draft, let the user correct it and require confirmation before committing financial/work records.
- Python/domain logic—not the LLM—calculates currency totals, balances, permissions and state transitions.
- Currency calculations use exact representation rather than binary floating point.
- Manual entry remains available if voice providers fail or credits run out.
- Provider keys stay server-side in ignored local environment files or host secret settings. Never paste keys into chat or commit them.
- Do not assume model capabilities, supported languages, endpoint paths, quotas or provider pricing; verify current official documentation and report uncertainty.

## 5. Scope priorities

### MVP first
1. User profile and mode.
2. Business sales/expense entries and summaries.
3. Worker work records, rates/amounts, advances and payment entries.
4. Deterministic calculation breakdowns.
5. Explicit invitation/acceptance and shared record states.
6. Voice transcription/extraction as a draft with confirmation.
7. History, authorization, security, tests and a reliable manual fallback.

### Later only with approval
- Full accounting, tax filing, statutory payroll, bank/UPI integrations, payment initiation, lending/credit scoring, automatic wage-recovery actions, broad admin tooling, or additional paid integrations.

## 6. Provider/credit approach

- Use Gnani only for approved speech operations; don't waste speech credits on reasoning.
- Keep speech providers behind backend adapters.
- Add per-user and per-IP usage limits, maximum audio size/duration, timeouts, bounded retries and usage accounting.
- Use TTS only when requested or useful; text output is sufficient for many interactions.
- Treat a mock, a local inference setup and a live hosted integration as different modes, clearly labelled in configuration and reports.
- If exact provider documentation or access is missing, ask the owner for access or work on an interface/mock without pretending integration is live.

## 7. Current implementation status

- **Codebase inspected:** Yes — 2026-10-27. The workspace contained only the six specification Markdown files plus `.freebuff/`. It was a greenfield project with no source code, no tests, no CI and no git repository.
- **Repository created:** Yes — 2026-10-27. `git init -b main`; initial commit `9a7bcce` contains the six specification documents and a root `.gitignore`. No remote is configured yet, so nothing has been pushed.
- **Frontend implementation:** Phase 1 shell implemented. React 19 + TypeScript 7 + Vite 8 + Tailwind 4. `npm run typecheck` and `npm run build` both pass.
- **Backend implementation:** Phase 1 foundation implemented. FastAPI 0.162 + Pydantic 2.14 + pydantic-settings. Health and capability endpoints verified over real HTTP.
- **Database:** None in use yet. No SQLAlchemy models, no migrations, no tables. `ML_DATABASE_URL` is validated for scheme only.
- **Authentication:** Not implemented. Provider not confirmed; this blocks Phase 2.
- **Gnani live integration:** **Not integrated and no request has ever been made.** Credentials, endpoints, supported languages and quotas remain unverified. A web research attempt on Gnani docs was cancelled by the user before returning results, so there is still no confirmed documentation reference in this repo.
- **Reasoning provider:** Not selected and not implemented. `ML_REASONING_MODE` defaults to `disabled`; `mock`/`local`/`live` are configuration labels only, with no adapter code behind them.
- **Deployment:** Not verified. Nothing has been deployed or pushed.
- **Tests:** 18 backend tests pass (`uv run pytest`: 18 passed, 0 failed). Frontend has **no automated test suite yet** — it is checked by `tsc --noEmit` and a production build only, which is not the same as tested behaviour.

Update each item with evidence after inspecting or changing the repository. Do not use “done” unless there is implementation evidence and, where appropriate, test/deployment verification.

## 8. Open decisions to revisit only when they block work

- Does one account support both Business and Worker modes, or is one primary role selected at onboarding?
- Which authentication provider and deployment platform will be used?
- Which initial language(s) have a verified voice pipeline and acceptable extraction accuracy?
- Which reasoning model/provider can the owner access within approved cost constraints?
- What are the actual Gnani credit/quota limits and how much should a user be allowed to consume?
- Is offline entry required for the first release?
- What retention/export behavior applies to shared history after unlinking or account deletion?

Do not block the whole project for every open decision. Proceed with reversible, clearly labelled defaults where safe; ask the owner only when a decision materially changes security, cost, data model or product behavior.

## 9. Session handoff template

At the end of each meaningful work session, update this section without deleting previous unresolved risks:

### Session 1 — 2026-10-27

- **Phase worked on:** Phase 0 (discover and plan) and Phase 1 (project foundation and design shell).
- **Files changed:** Created `.gitignore`, `README.md`, `backend/` (pyproject, `.env.example`, app package, tests) and `frontend/` (Vite + React + TS + Tailwind app shell, pages, components, API client). 54 files in the Phase 1 commit.
- **Tests/commands actually run:**
  - `cd backend && uv run pytest` → **18 passed**, 1 third-party deprecation warning.
  - `cd backend && uv run ruff check .` → **All checks passed**.
  - `cd backend && uv run ruff format --check .` → 14 files already formatted.
  - `cd backend && uv run uvicorn app.main:app --host 127.0.0.1 --port 8000` → started; `GET /api/v1/health` and `GET /api/v1/system/capabilities` both returned **HTTP 200** with expected JSON.
  - `cd frontend && npx tsc --noEmit` → exit 0.
  - `cd frontend && npm run build` → built successfully (286.86 kB JS / 18.72 kB CSS).
  - `cd frontend && npm run dev` → served on 127.0.0.1:5173; `GET /api/v1/health` through the Vite proxy returned the backend JSON, confirming the proxy works.
  - Browser check: `/` redirected to `/choose-mode`; choosing Business navigated to `/business`; dashboard rendered empty states; the capabilities fetch returned 200; no console errors.
  - Bundle check: `grep -o -i "gnani|api_key|apikey|secret" dist/assets/*.js` found only `api_key_configured` (a boolean field name). No provider name or credential value in the browser bundle.
- **Results:** Phase 1 exit gate met for the parts that can be verified here. Both apps start with documented commands, navigation works, no credential is reachable from the browser, and the lint/build checks pass.
- **Known defects / limitations:**
  - Tests run against SQLite, not PostgreSQL. No PostgreSQL server exists in this environment, so PostgreSQL behaviour is **unverified**.
  - The frontend has no automated tests; TypeScript and a build are its only checks.
  - Mode selection is a device-level `localStorage` value, not an account attribute.
  - `voice_enabled` is hardcoded `false` because no voice endpoints exist; it is not derived from provider state.
  - FastAPI/Starlette emit a deprecation warning about `httpx` vs `httpx2` in the test client. Harmless for now, worth revisiting.
  - Nothing has been pushed: no git remote is configured.
- **Credentials or external access still needed (never include the secret itself):** Gnani API access and official documentation; a decision on the authentication provider; a database host decision; an approved reasoning provider.
- **Next smallest safe step:** Obtain the answers below, then implement Phase 2 (authentication and authorization foundation) with the first real database models and migrations.

## 10. Decisions and assumptions made in Phase 1

Recorded so that later sessions can see what was assumed rather than approved.

- **Money representation (chosen, not yet used):** currency will be stored as integer minor units (paise) so SQLite and PostgreSQL behave identically and binary floating point is never used. No money code exists yet.
- **Local database:** SQLite is used for local development and tests because no PostgreSQL server is available here. PostgreSQL remains the production target; the settings module refuses to start in production with the development default.
- **Settings prefix:** all backend environment variables use the `ML_` prefix; secrets use Pydantic `SecretStr` so they are masked in logs and dumps.
- **Capability endpoint:** `GET /api/v1/system/capabilities` is deliberately unauthenticated and returns booleans and enum labels only — never a credential or a base URL.
- **Unsafe production config fails closed:** production requires a real database URL and explicit CORS origins, and disables the interactive docs.
- **CORS credentials disabled:** the API authenticates with bearer tokens, not cookies, so `allow_credentials` is `False`.
- **Mode storage key:** `mehnatledger.shell.mode` in `localStorage`, explicitly marked temporary until accounts exist.
- **Voice UI while unimplemented:** the voice action is rendered **disabled** with a plain explanation rather than as a button that silently does nothing.
- **Not-built screens:** every placeholder links to `/not-built` and states that nothing was saved.
- **No demo data:** no seed script, no fixtures inserted into any user-facing database, and no seeded accounts. Test fixtures use obviously fake values that never reach the application database.
