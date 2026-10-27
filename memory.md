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
- **Backend implementation:** Phase 1 foundation plus Phase 2 authentication. FastAPI 0.162 + Pydantic 2.14 + pydantic-settings + SQLAlchemy 2.1 + Alembic 1.20 + PyJWT 2.15. Health, capability and `/api/v1/me` endpoints verified over real HTTP.
- **Database:** SQLAlchemy engine/session layer and one Alembic migration (`profiles`) that has been run and reversed successfully against SQLite. **No PostgreSQL verification has happened.**
- **Authentication:** Implemented as Supabase token verification (JWKS asymmetric path plus legacy shared-secret path), a `get_current_identity` dependency, and an ownership-scoped profile repository. **Verified only with locally minted tokens**, so the live Supabase handshake, the real JWKS fetch and the real `aud` claim remain **unverified**. `ML_SUPABASE_URL` is still unset, so no request can currently be authenticated.
- **Gnani live integration:** **Not integrated and no request has ever been made.** Credentials, endpoints, supported languages and quotas remain unverified. A web research attempt on Gnani docs was cancelled by the user before returning results, so there is still no confirmed documentation reference in this repo.
- **Reasoning provider:** Not selected and not implemented. `ML_REASONING_MODE` defaults to `disabled`; `mock`/`local`/`live` are configuration labels only, with no adapter code behind them.
- **Deployment:** Not verified. Nothing has been deployed or pushed.
- **Tests:** 18 backend tests pass (`uv run pytest`: 18 passed, 0 failed). Frontend has **no automated test suite yet** — it is checked by `tsc --noEmit` and a production build only, which is not the same as tested behaviour.

Update each item with evidence after inspecting or changing the repository. Do not use “done” unless there is implementation evidence and, where appropriate, test/deployment verification.

## 8. Open decisions to revisit only when they block work

### Resolved by the owner on 2026-10-27

- **Authentication provider:** Supabase Auth. The owner deferred to the agent's recommendation, so this is a recommendation the owner accepted, not an independently stated preference. Recommended because `architecture.md` proposed it, it is a managed provider (so we do not hand-roll password hashing and reset flows), and it pairs with the chosen database.
- **Database host:** Supabase PostgreSQL.
- **Gnani access:** the owner states they **have** access and will configure keys in `backend/.env`. This has not been independently verified, and no request has been made. Credentials must never be pasted into chat.

### Still open

- **Git remote:** not supplied yet. Three commits exist locally and nothing has been pushed.
- **Supabase project:** does not exist yet. No URL, JWT secret or connection string has been provided, so no authentication or PostgreSQL code has been written or tested.
- Does one account support both Business and Worker modes, or is one primary role selected at onboarding?
- Which initial language(s) have a verified voice pipeline and acceptable extraction accuracy? The owner has access but no language has been confirmed as tested.
- Which reasoning model/provider can the owner access within approved cost constraints?
- What are the actual Gnani credit/quota limits and how much should a user be allowed to consume?
- Is offline entry required for the first release?
- What retention/export behavior applies to shared history after unlinking or account deletion?
- Deployment platform for the frontend and backend (not selected).

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
- **Next smallest safe step:** Create the Supabase project, put its values in `backend/.env`, and confirm whether it uses asymmetric signing keys — then re-run the suite and exercise a real sign-in.

### Session 2 — 2026-10-27 (continued)

- **Phase worked on:** Phase 2 (authentication and authorization foundation).
- **Pushed:** Remote `https://github.com/Saadkhan10412/MehnatLedger.git` added as `origin`; `main` pushed and verified (`refs/heads/main` == local HEAD).
- **Research done before coding:** read Supabase's official JWT and signing-key documentation. Two findings shaped the implementation: (a) the JWKS endpoint returns **no keys** unless the project uses asymmetric signing keys, and (b) Supabase's JWT payload reference does **not** list an `aud` claim, so enforcing an invented audience would have rejected every real token.
- **Tests/commands actually run:**
  - `uv run pytest` → **50 passed**, 0 failed (2 third-party warnings). Up from 18.
  - `uv run ruff check .` → All checks passed.
  - `uv run ruff format --check .` → 31 files already formatted.
  - `uv run alembic upgrade head` → applied `da06bf3679b5` successfully.
  - Migration verified by direct SQLite inspection: `profiles(id CHAR(32) PK, created_at, updated_at)` and **0 rows**.
  - Downgrade to `base` verified to remove the table (covered by a test).
  - Restarted uvicorn and called the API over real HTTP: `/api/v1/health` → 200; `/api/v1/me` with a bogus bearer token → **503** with a setup-requirement message, because no Supabase project is configured. That is deliberate: 503 states the truth instead of blaming the user's credential.
  - Startup log confirmed two honest warnings (no Supabase configured; local SQLite in use).
- **Known defects / limitations:**
  - **No live-provider verification.** Every auth test mints tokens from an in-process keypair and feeds the verifier an in-process JWKS, so only the network fetch is stubbed. The real Supabase handshake is untested and must not be described as working.
  - **PostgreSQL still unverified**, as is the Supabase pooler/direct connection choice.
  - The `aud` claim is **not enforced** by default. The real value should be read from an actual access token and then set in `ML_SUPABASE_JWT_AUDIENCE`.
  - No sign-in UI. The frontend has no way to obtain a token yet, so `/api/v1/me` is only reachable with a manually supplied token.
  - The capabilities endpoint does not yet report whether authentication is configured, so the UI cannot currently show that state.
  - Frontend still has no automated tests.
- **Credentials or external access still needed:** a Supabase project (URL, and either asymmetric signing keys with JWKS or the legacy secret), plus the signing configuration the project actually uses.
- **Decisions recorded during this phase:** the `profiles` table is named `profiles` (not `users`) to avoid confusion with Supabase's `auth.users`, which this app never writes to; the profile row stores **no** personal data beyond the auth subject; rows are created lazily on first authenticated request, race-safe via rollback-and-read on duplicate key.

### Session 3 — 2026-10-27 (live Supabase verification)

The owner supplied `ML_SUPABASE_URL` and a publishable key, written only to the
git-ignored `backend/.env`. **Verified live against project
`ybrubxbwiypjyenvjgfa`, not stubbed:**

- `GET /auth/v1/.well-known/openid-configuration` → **200**, and its `issuer`
  (`https://ybrubxbwiypjyenvjgfa.supabase.co/auth/v1`) **exactly matches** the
  issuer the settings module derives from the project URL.
- `GET /auth/v1/.well-known/jwks.json` → **200 with 1 key**: `kid=7f16acdd-e845-
  486d-897b-7bac43a16a45`, **`alg=ES256`**, `kty=EC`, `use=sig`,
  `key_ops=[verify]`. `id_token_signing_alg_values_supported` lists
  `['RS256','HS256','ES256']`, consistent with it.
- **This resolves the asymmetric-vs-legacy fork**: the project *does* use
  asymmetric signing keys, so the JWKS path is the correct one and Supabase's
  shared-secret warning path is not needed here.
- `claims_supported` **includes `aud`**, so enforcing an audience is legitimate
  for this project. Its exact *value* is not published anywhere, so it remains
  unset and must be read from a real access token.
- Only `authorization_code` and `refresh_token` grants are advertised in the
  OIDC document, which matters when the sign-in flow is built.

**Bug found and fixed by this verification:** a blank `ML_SUPABASE_JWT_SECRET=`
was wrapped by Pydantic in `SecretStr("")`, which compares `is not None`, so
`auth_mode` reported `shared_secret` and the verifier would have accepted tokens
signed with an **empty HMAC key**. Fixed with `env_ignore_empty=True` plus a
guarded `shared_secret_value` property that treats blank and whitespace-only as
unset; the publishable key is now held as `SecretStr` so it cannot reach a repr
or log. Regression tests added.

- **Tests/commands actually run:** `uv run pytest` → **55 passed** (was 50);
  `uv run ruff check .` and `ruff format --check .` → clean;
  `uv run python scripts/verify_supabase.py` → exit **2** (INCOMPLETE),
  3 PASS / 2 SKIP.
- **Still unverified:** any real access token (issuer/audience/round-trip),
  PostgreSQL, and a real user sign-in flow. No user account was created and no
  Supabase API that mutates data was called.
- **Next smallest safe step:** obtain a real access token, or authorization to
  create a throwaway test user, to complete the token check.

### Supabase research findings (verified 2026-10-27)

Read from official Supabase documentation. Recorded because the integration depends on
current provider behaviour that must not be guessed.

- Supabase currently provides **two** signing systems: the **legacy JWT secret** (one shared
  secret signing everything, no longer recommended) and the newer **Signing keys** system
  (asymmetric RSA/Elliptic-Curve keys, or a shared secret). Source:
  <https://supabase.com/docs/guides/auth/signing-keys>
- With asymmetric signing keys, the public key is published at a **JWKS discovery endpoint**
  (`/.well-known/jwks.json`). Verification is then local and fast, key rotation is automatic via
  discovery, and rotation does **not** force users to sign out. With the legacy shared secret,
  verification involves the Auth server and rotation can break components that verify with it.
- Supabase's guidance is to verify with `getClaims()`/the JWT verification guide. Both the JWKS
  and legacy-secret approaches exist, so the correct one depends on the project's actual settings —
  this must be checked in the dashboard, not assumed.
- **SQLAlchemy/connection strings:** stationary servers (VM, long-running container) should use the
  **direct** connection string. It maps to an **IPv6** address and will not work in an IPv4-only
  environment; the documented alternatives are the Supavisor pooler in **session** mode (port 5432)
  or the IPv4 add-on on a paid plan. Auto-scaling/serverless deployments should instead use the
  pooler in **transaction** mode (port 6543) with `NullPool`. Source:
  <https://supabase.com/kb/troubleshooting/using-sqlalchemy-with-supabase-FUqebT>
- The Gravity Index integration catalog does **not** carry Supabase, so no tracked setup link or
  install guidance was available from it. No setup URL has been provided or invented.

**Not verified:** that any Supabase project exists, that its signing configuration is asymmetric,
that the pooler/direct choice works from this machine, or that Supabase free tier limits suit this
project. None of these can be confirmed without the owner's project.

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
