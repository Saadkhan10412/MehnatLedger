import type { ReactNode } from 'react';

interface SummaryStatProps {
  label: string;
  /**
   * A formatted, server-calculated value. Pass the em dash (—) and a hint when
   * there are no underlying records: never display a fabricated amount.
   */
  value: string;
  hint?: string;
  labelSuffix?: ReactNode;
}

export function SummaryStat({ label, value, hint, labelSuffix }: SummaryStatProps) {
  return (
    <div>
      <p className="flex items-center gap-1.5 text-sm font-medium text-ink-muted">
        <span>{label}</span>
        {labelSuffix}
      </p>
      <p
        className="mt-1 text-2xl font-semibold tabular-nums text-ink"
        // Screen readers get the same context the sighted user sees.
        aria-hidden={value === '—'}
      >
        {value}
      </p>
      {hint ? <p className="mt-1 text-xs text-ink-muted">{hint}</p> : null}
      {value === '—' ? <p className="sr-only">{label}: nothing recorded yet.</p> : null}
    </div>
  );
}
