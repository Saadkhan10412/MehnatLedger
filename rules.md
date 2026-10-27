# MehnatLedger — Rules for the AI Coding Agent

These instructions are mandatory. They take precedence over convenience, speed and guesses.

## 1. Truthfulness and evidence

1. Never claim that a feature works, a test passed, a deployment succeeded or an API integration is live unless you actually verified it.
2. Distinguish **implemented**, **tested**, **mocked**, **blocked** and **not started** in reports.
3. Do not invent provider endpoints, SDK methods, supported languages, credentials, database states, environment variables or business requirements.
4. When provider documentation or credentials are unavailable, state the exact missing requirement. You may build an interface or clearly labelled mock, but never present it as a live integration.
5. If a test cannot run, say why and give the exact command/error. Do not replace failed verification with an assumption.

## 2. How to work with the product owner

1. Start by inspecting the existing repository, git status, project manifests, relevant source files and current tests. Do not assume a blank repository.
2. Before large changes, report what already exists and the proposed smallest safe step.
3. Ask the user for assistance when blocked by a required credential, a material product decision, a permission boundary, inaccessible documentation, a destructive action or a choice that could incur money.
4. Do not ask the user to decide minor implementation details that can safely follow this specification. Make the conservative choice, document it in `memory.md`, and continue.
5. Never ask for API keys to be pasted into chat. Tell the user how to configure them in an ignored local `.env` file or a hosting secret manager.
6. Do not repeat a question already answered in the current project documents. When requirements conflict, state the conflict and ask before choosing.
7. Keep progress reports concise and factual: what changed, what was tested, what remains and whether user input is required.

## 3. Cost and provider rules

1. No paid API, paid hosting upgrade, usage-based external service, web-search add-on or unexpected billing may be enabled without explicit product-owner approval.
2. Do not assume Gnani credits are unlimited or renewable. Add usage limits and a manual-entry fallback.
3. Do not replace a failing or unavailable provider with a paid provider automatically.
4. Keep reasoning separate from Gnani speech services. Use the approved reasoning provider or a documented local/mock implementation until the production choice is approved.
5. Never send user data to a provider unless the integration is approved and the data flow is documented.

## 4. Secrets and repository safety

1. Never commit API keys, access tokens, passwords, database credentials, private certificates or real personal data.
2. Do not place private credentials in React source, browser storage, frontend build-time environment variables, client bundles, logs, screenshots or test fixtures.
3. Keep `.env` ignored and provide `.env.example` with placeholders only.
4. If a secret is found in tracked files or Git history, stop and alert the user; recommend immediate revocation/rotation. Do not claim deleting the file removes the secret from history.
5. Do not run destructive commands, force-push, reset user changes, overwrite substantial files or alter production data without first inspecting the impact and getting explicit approval where needed.

## 5. Security and privacy rules

1. Enforce authorization on the backend for every private record and action. Frontend route guards are not a security boundary.
2. Never trust a caller-supplied user ID to determine ownership.
3. A Business-Worker link must require explicit acceptance. It does not grant access to unrelated private ledger entries.
4. Do not silently decide disputed wage/work entries or erase meaningful shared-record history.
5. Voice output is a proposal until confirmed by the user. AI extraction must not write financial records directly.
6. Use deterministic code for balances, totals, permissions and state transitions. LLM output is untrusted input and must be schema-validated.
7. Minimize collection and retention of audio, transcripts and identifying information. Do not train on user data by default.
8. Do not log secret values, auth tokens, complete raw audio or unnecessary private content.

## 6. Engineering standards

1. Keep modules focused and typed; reuse established patterns in the repository.
2. Validate all client input on the backend. Use clear schemas, database migrations and stable error responses.
3. Money must use exact decimal/minor-unit handling, never binary floating-point arithmetic.
4. Important multi-step writes must be transactional. Retryable writes must be protected against duplicates.
5. Add tests for new business logic and security boundaries. Test the failure path, not only the happy path.
6. Do not over-engineer. Do not add frameworks or dependencies without a concrete need.
7. Keep manual entry usable when speech services are offline, disabled or out of credits.
8. Do not silently convert a prototype mock into production-looking data. All seed/demo data must be clearly identified and separate from real users.

## 7. Phase discipline

1. Follow `phases.md` in order unless a documented dependency justifies a different sequence.
2. At the beginning of a phase, inspect the relevant code and state the phase goal.
3. Before moving on, run the phase's checks and compare them to its exit gate.
4. Do not mark a phase complete if required tests are failing, a security boundary is untested, or a live integration is mocked but described as live.
5. Update `memory.md` after each meaningful phase: completed work, verification, known limitations, decisions and next action. Do not erase unresolved issues just to make status look clean.
6. If the context or session changes, reread `memory.md`, `phases.md` and the relevant source before continuing.

## 8. Final response format

When reporting progress, include:
- **Completed:** concrete files/features changed.
- **Verified:** exact test/build/lint commands actually run and their actual outcomes.
- **Not verified / blocked:** anything not tested or dependent on missing credentials/services.
- **User input needed:** only the decisions or access that genuinely block progress.
- **Next step:** one clear, safe action.

Never say “everything is done” when only the UI, mock data or one happy path has been implemented.
