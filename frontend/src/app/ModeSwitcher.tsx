import { useNavigate } from 'react-router-dom';

import { MODE_LABELS, modeHomePath, useMode, type AppMode } from '../features/mode/ModeContext';

const MODES: AppMode[] = ['business', 'worker'];

interface ModeSwitcherProps {
  className?: string;
}

/**
 * Segmented control for switching mode.
 *
 * Note (Phase 1): this is a device-level preference because accounts do not
 * exist yet. design.md section 3 expects mode switching to be gated on the
 * account having both modes enabled; that gate lands with authentication.
 */
export function ModeSwitcher({ className = '' }: ModeSwitcherProps) {
  const { mode, setMode } = useMode();
  const navigate = useNavigate();

  const choose = (next: AppMode) => {
    setMode(next);
    navigate(modeHomePath(next));
  };

  return (
    <div
      role="group"
      aria-label="Choose mode"
      className={`inline-flex rounded-xl border border-line-strong bg-surface-raised p-0.5 ${className}`}
    >
      {MODES.map((candidate) => {
        const selected = mode === candidate;
        return (
          <button
            key={candidate}
            type="button"
            aria-pressed={selected}
            onClick={() => choose(candidate)}
            className={`min-h-9 rounded-lg px-3 text-sm font-medium transition-colors ${
              selected ? 'bg-primary text-white' : 'text-ink-muted hover:text-ink'
            }`}
          >
            {MODE_LABELS[candidate]}
          </button>
        );
      })}
    </div>
  );
}
