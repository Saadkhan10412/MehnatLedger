# MehnatLedger — Product Requirements Document (PRD)

**Document status:** Working specification v1  
**Product:** MehnatLedger  
**Audience:** Product owner, designer, AI coding agent, developers and testers  
**Purpose:** Define what to build, for whom, and how success will be checked.

> **Truth rule:** This document records the current product direction, not proof that any feature has been implemented. Treat items labelled *Proposed* or *Open* as decisions to validate, not facts.

## 1. Product summary

MehnatLedger is a voice-first recordkeeping app for small Indian businesses/shopkeepers and daily-wage or informal workers. It helps people record everyday business entries and work/payment records by speaking naturally, while still providing ordinary forms for users who do not want or cannot use voice.

The product has two experiences:

- **Business Mode:** a small business owner records basic daily sales, expenses and work-related records.
- **Worker Mode:** a worker records days/shifts worked, agreed or reported wages, advances and payments received.
- **Shared Hisaab:** where a business and worker explicitly connect their accounts, they can review the specific work/payment records shared between them. A record can be proposed, acknowledged, disputed or marked paid/settled as appropriate. Neither party's private records are exposed just because accounts are linked.

MehnatLedger is a recordkeeping and reconciliation aid. It is not a court, legal authority, bank, full accounting package, payroll-compliance system or guarantee of evidence admissibility.

## 2. Problem statement

Small businesses and workers may rely on memory, loose paper, notebooks or separate informal messages to track daily activity. Records can be incomplete, hard to find, or different between the two parties. Typing detailed entries can also be inconvenient for users who prefer speaking in a supported language.

MehnatLedger aims to lower the effort of creating and reviewing records and make disagreements visible instead of silently deciding which account is correct.

## 3. Target users

### 3.1 Small business owner / shopkeeper

Needs to:
- Quickly record daily cash and UPI sales totals and business expenses.
- Maintain simple records of workers' shifts, wage amounts, advances and payments where relevant.
- Review a daily or date-range summary.
- Use voice when helpful and edit entries before they are saved.

### 3.2 Daily-wage / informal worker

Needs to:
- Keep a personal record of dates or shifts worked.
- Record the wage rate or amount they believe was agreed, advances and payments received.
- See a calculated balance based on recorded entries.
- Review or dispute shared records without losing their own independent history.
- Export or share a user-approved summary when useful.

### 3.3 Product administrator (limited MVP role)

Needs to manage technical support and investigate errors without unrestricted, routine access to private records. Administrative access must be permissioned and auditable. Do not build a broad admin console unless needed for the MVP.

## 4. Product goals

1. Make routine records quick to create with voice or forms.
2. Make calculations deterministic, explainable and testable.
3. Give each user control over their own data.
4. Let business and worker records be compared only through an explicit, accepted sharing relationship.
5. Preserve usefulness when voice AI is unavailable or credits are exhausted.
6. Never require end users to provide their own Gnani or reasoning-model API keys.

## 5. Non-goals for the MVP

Do **not** implement these unless the product owner explicitly approves a later scope change:
- Full double-entry accounting, GST returns, invoicing/tax filing or statutory payroll compliance.
- Bank account linking, automatic UPI transaction ingestion, payment initiation or custody of funds.
- Automated wage recovery, legal claims, credit scoring, lending or employment decisions.
- Public profiles or public leaderboards for workers/businesses.
- Automatic messaging to employers or workers without a user's explicit confirmation.
- AI deciding which party is telling the truth.
- Unrestricted AI chat, autonomous financial actions or unexplained balance adjustments.
- Paid hosted AI, paid search, paid enrichment or another billable service without explicit approval from the product owner.

## 6. MVP functional requirements

### FR-01: Account and profile
- A user can sign in through the authentication method approved for the deployment.
- A user selects a primary mode (Business or Worker); a user may have both modes only if that product behavior is deliberately implemented and clearly separated.
- Store only profile fields needed for the service. Do not assume Aadhaar, bank details or other sensitive identifiers are required.

### FR-02: Business ledger
- Create, read and correct dated sales and expense records.
- Sales may include a payment-method breakdown such as cash and UPI, but these are user-entered claims unless verified by another source.
- Show totals for a selected day or date range.
- A record should include amount, category/type, effective date, author, creation time and optional note.
- Use decimal-safe monetary representation; never use binary floating point for currency calculations.

### FR-03: Worker ledger
- Record a work date/shift, hours or units when applicable, a reported/agreed rate, wage amount, advances and payments received.
- Calculate any displayed outstanding balance using explicit business rules in backend code.
- Show the underlying entries that explain a balance; never present an unexplained AI-generated amount.
- Let a user correct an unshared personal draft. Changes to shared records must retain a clear history.

### FR-04: Shared Hisaab and consent
- A business-worker relationship is created only through an explicit invitation and acceptance by both accounts.
- Either party can stop sharing future records through a documented unlink flow. The system must clearly explain how prior shared records are retained or restricted; do not silently delete an audit trail.
- Each shared record identifies who created it, the date it refers to, the time it was recorded and its current state.
- States must distinguish at least: **Proposed**, **Acknowledged**, **Disputed**, and **Paid/Settled** where applicable. These states are not interchangeable; payment status and record-approval status should be modeled separately where required.
- A party can dispute a record and add an optional explanation. A dispute does not automatically determine fault.
- Do not expose a user's unrelated sales, expenses, other workers, notes or private records to the linked counterparty.

### FR-05: Voice entry
- The user deliberately starts recording and can stop/cancel it.
- The app sends audio to the backend; the browser must never receive the provider secret.
- Show the recognized transcript and proposed structured fields before any financial record is committed.
- Allow correction of names, dates, hours, rates and amounts.
- Require explicit confirmation before committing a voice-generated financial or work record.
- If transcription, reasoning or text-to-speech is unavailable, show an understandable error and keep manual entry available.

### FR-06: Speech and reasoning provider separation
- Integrate Gnani speech-to-text (Prisma) and text-to-speech (Timbre) through server-side adapters, using the exact provider API documentation and credentials supplied/approved for the project.
- Use a separate reasoning/extraction provider. A local/open-weight model may be explored, but the selected model and production hosting plan are not yet confirmed.
- Do not assume hosted APIs or model credits are free. Do not add a paid provider or enable billing without explicit approval.
- Business calculations and authorization checks must not depend on an LLM.

### FR-07: History and export
- Users can search/filter their own records by date/type and review details.
- Provide a basic export (for example CSV) only after handling access control and formula-injection risks.
- Shared exports require a clear user action and must include only the selected, authorized records.

### FR-08: Usage and reliability controls
- Add authentication, server-side authorization and per-user/per-IP rate limits for expensive voice operations.
- Track usage counts and clear errors without logging API keys, full sensitive transcripts or unnecessary personal data.
- Provide a way to disable voice features while keeping manual bookkeeping usable.

## 7. Core data concepts

- **User:** authenticated person and profile.
- **BusinessProfile:** information needed for a small business ledger.
- **WorkerProfile:** information needed for a worker's personal work/payment records.
- **BusinessWorkerLink:** bilateral relationship created by invitation and acceptance.
- **LedgerEntry:** sales, expense or other supported business record.
- **WorkRecord:** date/shift, hours or units, wage terms and associated records.
- **PaymentRecord:** an independently recorded payment/advance with date, amount, method (optional) and recorder.
- **SharedRecordState / AuditEvent:** history of proposals, acknowledgements, disputes, corrections and settlements.
- **VoiceDraft:** temporary transcript and proposed fields awaiting confirmation; it should expire or be removed according to a documented retention policy.

These are conceptual entities. The architecture document may refine them after inspecting the existing repository, but must not remove the consent and audit requirements.

## 8. Non-functional requirements

- **Security:** users can access only their own records and the specific records explicitly shared with them.
- **Privacy:** collect the minimum data needed; explain what is shared; do not use private records for model training by default.
- **Reliability:** voice failure must not corrupt records; retrying requests should not create duplicate entries.
- **Accessibility:** mobile-first layout, readable text, clear labels, touch-friendly controls and a non-voice alternative to every voice action.
- **Localization:** design for Indian-language labels and speech. Initially enable only languages confirmed by implementation tests; do not claim broad language support without evaluation.
- **Auditability:** record meaningful changes to shared entries without silently overwriting history.
- **Maintainability:** typed API contracts, database migrations, automated tests and documented configuration.

## 9. Acceptance criteria

The MVP is acceptable only when all of the following pass:
1. A business user can add and review a sales record and an expense record.
2. A worker can add a work record, advance and payment, and see a deterministic balance with its component entries.
3. Two accounts cannot access each other's private records through direct API calls.
4. Shared records require both parties to establish the relationship; a user can acknowledge or dispute a record.
5. Voice-generated records are drafts until the user confirms them.
6. Gnani credentials are never shipped to the browser or committed to source control.
7. Voice quota/provider failures leave manual entry usable and do not create duplicate or partial financial records.
8. Automated tests cover monetary arithmetic, permissions, state transitions and key failure paths.
9. Setup instructions work from a clean checkout using placeholders, without real credentials.
10. The agent reports exactly which tests it ran and their actual results.

## 10. Open product decisions

Keep these visible and ask the product owner when a decision materially affects implementation:
- Which authentication option and deployment host will be used?
- Which languages must be supported in the first demo, based on provider capability and testing?
- Which reasoning model/provider will be used for the prototype and, separately, for production?
- How many Gnani credits are available and what usage budget should be enforced?
- Should one account support both Business and Worker modes in the MVP?
- What precise retention/export behavior is desired for shared records after an account unlinks?
- Is offline entry required for the first release, or is online-only acceptable?
