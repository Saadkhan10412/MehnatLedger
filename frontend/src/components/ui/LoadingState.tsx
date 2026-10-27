interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = 'Loading…' }: LoadingStateProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-center gap-3 rounded-[var(--radius-card)] border border-line bg-surface-raised px-4 py-6 text-sm text-ink-muted"
    >
      <span
        aria-hidden="true"
        className="size-4 animate-spin rounded-full border-2 border-line-strong border-t-secondary"
      />
      <span>{message}</span>
    </div>
  );
}
