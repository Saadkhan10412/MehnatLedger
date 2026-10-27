/**
 * Single source of truth for features that are deliberately NOT implemented yet.
 *
 * Every screen that links to one of these must tell the user plainly that the
 * action does not save anything, so a placeholder is never mistaken for a
 * working feature.
 */
export interface PlannedFeature {
  /** What the user was trying to do, in their words. */
  feature: string;
  /** Which phase of phases.md will deliver it. */
  phase: string;
}

export const PLANNED_FEATURES = {
  addSale: { feature: 'Recording a sale', phase: 'Phase 3 — Core individual ledgers' },
  addExpense: { feature: 'Recording an expense', phase: 'Phase 3 — Core individual ledgers' },
  addWorkRecord: { feature: 'Recording a work day', phase: 'Phase 3 — Core individual ledgers' },
  addPayment: { feature: 'Recording a payment or advance', phase: 'Phase 3 — Core individual ledgers' },
  balanceDetail: { feature: 'Viewing the calculation behind a balance', phase: 'Phase 3 — Core individual ledgers' },
  history: { feature: 'Searching and filtering history', phase: 'Phase 3 — Core individual ledgers' },
  export: { feature: 'Exporting records', phase: 'Phase 3 — Core individual ledgers' },
  linkAccount: { feature: 'Linking a business and worker account', phase: 'Phase 4 — Shared Hisaab and dispute workflow' },
  voice: { feature: 'Voice entry', phase: 'Phase 5 — Voice draft pipeline and AI provider adapters' },
  signIn: { feature: 'Creating an account and signing in', phase: 'Phase 2 — Authentication and authorization foundation' },
} as const satisfies Record<string, PlannedFeature>;

export type PlannedFeatureKey = keyof typeof PLANNED_FEATURES;

export function notBuiltPath(key: PlannedFeatureKey): string {
  const { feature, phase } = PLANNED_FEATURES[key];
  const params = new URLSearchParams({ feature, phase });
  return `/not-built?${params.toString()}`;
}
