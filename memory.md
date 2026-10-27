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

- **Codebase inspected:** Not yet recorded. The next agent must inspect the actual repository before assuming its state.
- **Frontend implementation:** Unknown / not verified.
- **Backend implementation:** Unknown / not verified.
- **Database/migrations:** Unknown / not verified.
- **Authentication:** Provider and implementation not confirmed.
- **Gnani live integration:** Not verified; do not assume API credentials, credits, endpoints or a successful request exist.
- **Reasoning provider:** Not selected for production.
- **Deployment:** Not verified.
- **Tests:** No test results are asserted by this memory file.

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

- **Date/session:** YYYY-MM-DD or an accurate current value.
- **Phase worked on:**
- **Files changed:**
- **Tests/commands actually run:**
- **Results:**
- **Known defects / limitations:**
- **Credentials or external access still needed (never include the secret itself):**
- **Next smallest safe step:**
