import { Button } from './Button';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
}

/**
 * Error state for failed requests.
 *
 * `message` should always be a safe, user-facing sentence. Raw server
 * responses and stack traces must never be rendered here.
 */
export function ErrorState({
  title = 'Something went wrong',
  message,
  onRetry,
  retryLabel = 'Try again',
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className="rounded-[var(--radius-card)] border border-danger/30 bg-danger-soft px-4 py-5"
    >
      <p className="text-sm font-semibold text-danger">{title}</p>
      <p className="mt-1 text-sm text-ink">{message}</p>
      {onRetry ? (
        <div className="mt-4">
          <Button variant="secondary" size="sm" onClick={onRetry}>
            {retryLabel}
          </Button>
        </div>
      ) : null}
    </div>
  );
}
