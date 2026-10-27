import type { ReactNode } from 'react';

interface EmptyStateProps {
  /** Short, plain-language statement of what is missing. */
  title: string;
  /** What the user can do next. */
  description?: string;
  action?: ReactNode;
}

/**
 * Shown wherever a list or total has no real records behind it.
 *
 * This project intentionally never seeds the application with invented
 * records, so empty states are the normal first experience.
 */
export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="rounded-[var(--radius-card)] border border-dashed border-line-strong bg-surface-raised px-4 py-6 text-center">
      <p className="text-sm font-medium text-ink">{title}</p>
      {description ? <p className="mx-auto mt-1 max-w-prose text-sm text-ink-muted">{description}</p> : null}
      {action ? <div className="mt-4 flex justify-center">{action}</div> : null}
    </div>
  );
}
