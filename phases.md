# MehnatLedger — Implementation Phases and Completion Gates

**Purpose:** Build in small, verifiable steps. Every phase must leave the repository in a known state. Use `memory.md` as the current handoff record.

## Phase 0 — Discover and plan

### Tasks
- Inspect the repository, current branch/status, manifests, existing app, tests and ignored files.
- Identify the actual coding agent/runtime capabilities and available commands without assuming tools exist.
- Read `prd.md`, `architecture.md`, `rules.md`, `design.md` and `memory.md`.
- Compare the existing implementation with the MVP; report what already exists, what is missing and any conflicts.
- Check whether official Gnani documentation and credentials are available **without exposing secrets**.

### Exit gate
- A concise repo/stack report exists.
- No existing user work has been overwritten.
- Critical questions and external blockers are explicit.
- A minimal next-phase plan is proposed. Ask the user only for decisions that block safe progress.

## Phase 1 — Project foundation and design shell

### Tasks
- Establish or preserve the frontend/backend structure and local development commands.
- Create typed configuration loading and `.env.example`; ensure `.env` and secret files are ignored.
- Implement the responsive app shell, navigation, Business/Worker mode selection and design tokens from `design.md`.
- Use clearly labelled empty/loading/error states. Do not fake successful data persistence.

### Exit gate
- Frontend and backend start using documented commands.
- Basic navigation works on mobile and desktop widths.
- No private credentials are bundled into the frontend.
- Lint/build checks that exist in the repository pass, or blockers are documented.

## Phase 2 — Authentication and authorization foundation

### Tasks
- Implement or integrate the selected authentication provider; confirm the decision if it materially differs from the proposal in `architecture.md`.
- Establish user identity/profile and server-side current-user resolution.
- Add authorization helpers and ownership-scoped query patterns.
- Add database migrations and a minimal isolated test setup.

### Exit gate
- An authenticated user can access their profile.
- Anonymous/invalid requests are rejected.
- Automated tests show one user's private data cannot be fetched by another user.
- No production secrets are required for local setup beyond clearly documented placeholders.

## Phase 3 — Core individual ledgers

### Tasks
- Implement the Business Mode sales/expense CRUD and daily/date-range summaries.
- Implement Worker Mode work entries, rates/amounts, advances and payment entries.
- Implement deterministic, exact monetary calculations in backend domain services.
- Add history/filter screens and clear validation/errors.
- Add tests for arithmetic, rounding, dates, duplicate submissions and permissions.

### Exit gate
- Business and worker records persist in the database and survive reloads.
- Balances can be explained by the entries included in the calculation.
- Invalid amounts and unauthorized record access are rejected server-side.
- Tests cover the core calculations and CRUD paths.

## Phase 4 — Shared Hisaab and dispute workflow

### Tasks
- Implement invitations and explicit acceptance for business-worker relationships.
- Implement shared record proposals, acknowledgment and dispute actions.
- Separate record review state from payment state where needed.
- Maintain an auditable correction/state history.
- Ensure linked users can access only records explicitly in the sharing scope.

### Exit gate
- Neither side can link accounts without the required consent.
- Private unrelated records remain private.
- Disputes remain visible and are not silently resolved by the app.
- Tests cover invitation, access control and valid/invalid state transitions.

## Phase 5 — Voice draft pipeline and AI provider adapters

### Tasks
- Implement a manual-entry-first voice interaction with start/stop/cancel controls.
- Create provider interfaces for speech-to-text, reasoning/extraction and text-to-speech.
- Integrate Gnani Prisma/Timbre only using current official docs and configured credentials.
- Use an approved reasoning provider; local model, mock and live provider modes must be clearly distinguishable.
- Parse model results into strict schemas, validate them, show a draft and require confirmation before saving.
- Add quotas, rate limits, timeouts, bounded retries and an opt-out/manual fallback.

### Exit gate
- No secret appears in browser code or responses.
- Provider failure, missing keys and quota exhaustion do not break manual entry.
- AI-generated fields are reviewed before a financial record is committed.
- Tests cover malformed model output, invalid audio, timeout, duplicate confirmation and quota rejection.
- Any untested/live-provider-dependent step is explicitly marked unverified.

## Phase 6 — Usability and accessibility

### Tasks
- Polish the core business and worker workflows using `design.md`.
- Verify keyboard navigation, focus visibility, label clarity, contrast, touch target sizes and responsive behavior.
- Provide readable transcript/field confirmation and a non-voice alternative for voice actions.
- Review empty states and error messages for non-technical users.

### Exit gate
- Core workflows can be completed without voice.
- Major pages are usable at narrow mobile widths and desktop widths.
- No key action is available only through color, icon or audio cues.

## Phase 7 — Security, privacy and reliability review

### Tasks
- Review every endpoint for authentication, ownership and shared-scope authorization.
- Review logs, file handling, voice quotas, database constraints, migrations and dependency configuration.
- Add integration tests for cross-user access and shared-record boundaries.
- Verify secrets are ignored and absent from tracked files; do not print secrets to check this.
- Document retention for temporary voice data and the current data deletion/export behavior.

### Exit gate
- No known critical authorization defect remains unresolved.
- Required tests pass.
- Security limitations and data-retention behavior are documented accurately.
- Any unresolved material risk is reported to the user instead of concealed.

## Phase 8 — Deployment and handoff

### Tasks
- Document local setup from a clean clone.
- Configure separate frontend/backend deployment and server-side secrets; do not deploy keys in frontend settings.
- Run migrations and production build checks in the intended environment where access is available.
- Configure HTTPS, allowed origins, rate limits, usage controls, backups and health checks as appropriate to the chosen host.
- Provide a demo workflow with visibly labelled demo data, if needed.

### Exit gate
- Clean setup instructions are reproducible.
- Deployment is called successful only if actually deployed and checked.
- The handoff lists exact commands/tests run, known limitations, costs/quotas and missing integrations.
- `memory.md` reflects the real implementation state and the next action.

## Rules for phase completion

- Do not skip gates silently.
- A UI-only demo is not a complete backend integration.
- A mock provider is not a live Gnani integration.
- A test suite that was written but not run must be reported as unrun.
- If a phase is blocked by access, credentials or a major user decision, finish safe independent work, record the blocker, and ask the user for the minimum required assistance.
