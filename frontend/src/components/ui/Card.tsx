import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  /** Renders as a section with an accessible heading when provided. */
  title?: string;
  description?: string;
  className?: string;
}

export function Card({ children, title, description, className = '' }: CardProps) {
  return (
    <section
      className={`rounded-[var(--radius-card)] border border-line bg-surface-raised p-4 shadow-sm sm:p-5 ${className}`}
    >
      {title ? <h2 className="text-base font-semibold text-ink">{title}</h2> : null}
      {description ? <p className="mt-1 text-sm text-ink-muted">{description}</p> : null}
      <div className={title || description ? 'mt-4' : ''}>{children}</div>
    </section>
  );
}
