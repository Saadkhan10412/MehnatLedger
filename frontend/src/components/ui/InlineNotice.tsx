import type { ReactNode } from 'react';

export type NoticeTone = 'info' | 'warning' | 'danger' | 'success';

const TONES: Record<NoticeTone, string> = {
  info: 'border-secondary/25 bg-secondary-soft text-ink',
  warning: 'border-warning/25 bg-warning-soft text-ink',
  danger: 'border-danger/30 bg-danger-soft text-ink',
  success: 'border-primary/25 bg-primary-soft text-ink',
};

/** Text labels are always rendered, so status is never colour-only. */
const TONE_LABELS: Record<NoticeTone, string> = {
  info: 'Note',
  warning: 'Attention',
  danger: 'Problem',
  success: 'Confirmed',
};

interface InlineNoticeProps {
  tone?: NoticeTone;
  title?: string;
  children: ReactNode;
  /** Hide the small tone label when the surrounding copy already says it. */
  showToneLabel?: boolean;
}

export function InlineNotice({
  tone = 'info',
  title,
  children,
  showToneLabel = true,
}: InlineNoticeProps) {
  return (
    <div className={`rounded-[var(--radius-card)] border px-4 py-3 text-sm ${TONES[tone]}`}>
      <p className="font-semibold">
        {showToneLabel ? <span className="sr-only">{TONE_LABELS[tone]}: </span> : null}
        {title ?? TONE_LABELS[tone]}
      </p>
      <div className="mt-1 text-ink-muted">{children}</div>
    </div>
  );
}
