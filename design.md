# MehnatLedger — Design Specification

**Status:** Proposed visual and interaction direction v1  
**Priority:** Clarity, trust, mobile usability and easy correction over visual complexity.

## 1. Product design principle

MehnatLedger should feel like a simple, reliable digital hisaab notebook—not a complex accounting dashboard and not a chatbot pretending to be an accountant. Users should quickly know what was recorded, who recorded it, what is shared and what still needs confirmation.

## 2. Visual direction

- **Overall style:** clean, friendly, practical, mobile-first, light theme by default.
- **Base surfaces:** warm off-white or very light neutral; white surfaces for forms and records.
- **Primary text:** dark charcoal/navy with sufficient contrast.
- **Primary accent:** green/teal for normal positive actions and confirmed status.
- **Secondary accent:** muted blue for neutral navigation and informational states.
- **Warning:** amber for pending review or attention.
- **Error/dispute:** red, paired with a text label and icon; never rely on color alone.
- Avoid excessive gradients, glass effects, animation, dense tables or tiny controls. Use a small consistent spacing scale, rounded cards and restrained shadows.
- Do not invent or use a final logo without approval. Use a text wordmark in the prototype.

## 3. Information architecture

### Common entry points
- Sign in / create account.
- Choose Business Mode or Worker Mode, or switch modes only if the account has both enabled.
- Home/dashboard.
- Add record (form or voice).
- History.
- Shared Hisaab (only for users with an accepted relationship).
- Profile, language and privacy settings.

### Business Mode navigation
- **Home:** today's totals, quick actions and a compact recent-activity list.
- **Add sale:** amount, date, optional cash/UPI breakdown and note.
- **Add expense:** amount, category, date and optional note.
- **Workers:** only workers connected through the explicit relationship process; show limited relevant summaries.
- **Shared Hisaab:** proposed, acknowledged, disputed and paid/settled items.
- **History:** filters and record details.

### Worker Mode navigation
- **Home:** recent work, recorded payments and a clearly labelled calculated balance if enough entries exist.
- **Add work record:** date/shift, hours or units, rate/amount and note.
- **Add payment/advance:** amount, date, optional method and note.
- **Shared Hisaab:** records explicitly shared by a connected business.
- **History:** personal and shared records clearly distinguished.

## 4. Voice interaction design

1. A large, labelled **Record by voice** action is visible where it meaningfully speeds up entry.
2. Explain microphone use before the first recording. Request browser permission only when the user activates recording.
3. Provide start, stop and cancel controls. Display a recording indicator and elapsed time where practical.
4. After transcription, show both the transcript and extracted fields. Highlight uncertain or missing fields rather than guessing silently.
5. The user can edit each field before save. Amounts, dates, names and record type receive particular attention.
6. Provide explicit **Confirm and save**, **Edit**, and **Cancel** actions. Do not save merely because transcription finished.
7. Offer optional spoken read-back. Respect mute and voice-off preferences.
8. If voice fails or the quota is exhausted, explain this briefly and offer manual entry without losing the user's work.
9. Never keep recording in the background or send audio without a clear user action.

## 5. Record cards and statuses

Every record card should make the following easy to identify:
- Record type and amount.
- Date the entry refers to.
- Person who recorded it.
- Personal vs shared label.
- Approval state and payment state, displayed separately when both apply.
- A route to view the component entries behind a total.

Use these state labels consistently:
- **Proposed:** recorded by one party, waiting for the other party's review.
- **Acknowledged:** the relevant other party confirmed the details as displayed.
- **Disputed:** at least one party has questioned the record; show that it needs resolution.
- **Paid / Settled:** use only when a payment or settlement event is actually recorded according to product rules. Do not infer it from acknowledgment.

Acknowledgment must not be described as a legal guarantee. A dispute should have a readable explanation and should not erase the original event.

## 6. Key screens

### 6.1 Sign-in and onboarding
- Plain language, minimal fields and clear privacy explanation.
- Ask for mode and only information essential to the chosen workflow.
- Do not demand government IDs, bank credentials or a shop address unless the approved product scope demonstrates a need.

### 6.2 Business dashboard
- Today's sales and expenses as separate totals.
- Clear distinction between sales, expense and net difference; do not label a simple difference as formal profit unless all required costs/accounting assumptions are handled.
- Quick actions: Add sale, Add expense, Record work/payment, Record by voice.
- Recent activity and any shared records awaiting review.

### 6.3 Worker dashboard
- Recent work records, recent payments and displayed balance with a way to inspect the calculation.
- Quick actions: Add work, Record payment/advance, Review shared record, Record by voice.
- Never present a disputed amount as an undisputed entitlement.

### 6.4 Voice review
- Transcript panel.
- Structured editable fields.
- Validation messages next to the field, not hidden in a toast only.
- Clear confirmation and cancellation.
- Status indicating whether AI is processing, unavailable or disabled without exposing provider secrets/technical internals.

### 6.5 Shared record detail
- Timeline of proposal, acknowledgment, dispute, correction and payment events.
- Who made each change and when.
- Actions available to the current user based on state and permissions.
- No action that silently changes the counterparty's private ledger.

### 6.6 History and export
- Search or filter by date and type.
- Good empty states with a next action.
- Exports must clearly state whether they include personal or shared records and should include only user-authorized entries.

## 7. Components and interaction patterns

Reusable candidates:
- `AppShell`, `ModeSwitcher`, `PageHeader`, `BottomNavigation` for mobile.
- `PrimaryAction`, `VoiceRecordButton`, `RecordingStatus`, `TranscriptReview`.
- `MoneyAmount`, `DateField`, `RecordTypeSelector`, `FormError`.
- `LedgerEntryCard`, `BalanceBreakdown`, `SharedStatusBadge`, `RecordTimeline`.
- `EmptyState`, `LoadingState`, `ErrorState`, `ConfirmationDialog`.

Do not create a component library for its own sake. Extract shared components when they serve at least two real screens or improve consistency.

## 8. Accessibility and localization

- Use semantic HTML, visible keyboard focus, labels associated with inputs and sensible heading hierarchy.
- Ensure color contrast and touch targets are adequate. Do not use color alone to communicate status.
- Provide text alternatives for voice-only content and readable error messages for audio failures.
- Keep text concise and use familiar wording. Avoid accounting jargon unless it is explained.
- Design for longer translations and code-mixed user input. Do not claim a language is supported until the actual transcription/TTS path has been tested for that language.

## 9. Responsive behavior

- Optimize for narrow phone widths first; forms should fit without horizontal scrolling.
- Use single-column layouts on mobile and wider summary panels only when there is space.
- Keep the main action easy to reach but do not obstruct form fields or screen readers.
- On desktop, use a sidebar only if it improves navigation; don't let the desktop layout create a different set of features.

## 10. Design quality gate

Before accepting a screen, verify:
- The user can tell what the page is for within a few seconds.
- The primary next action is obvious.
- Every amount has context and, where applicable, a breakdown.
- Personal/shared and proposed/confirmed/disputed states are distinguishable.
- Voice data is reviewed before saving.
- Loading, error, empty and success states exist.
- The same workflow remains possible without AI/voice.
