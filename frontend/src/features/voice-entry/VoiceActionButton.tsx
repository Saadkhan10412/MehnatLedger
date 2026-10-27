import { Link } from 'react-router-dom';

import { Button } from '../../components/ui/Button';
import { notBuiltPath, PLANNED_FEATURES } from '../../app/plannedFeatures';
import type { AsyncState } from '../capabilities/useCapabilities';

interface VoiceActionButtonProps {
  /** Result of the capability check; never assumed to be available. */
  capabilitiesState: AsyncState;
  voiceEnabled: boolean;
}

/**
 * Voice entry control.
 *
 * design.md section 4 requires a visible voice action, and phase 5 requires
 * manual entry to remain usable whenever voice is unavailable. Until the voice
 * pipeline exists in Phase 5, the control is shown disabled with a plain
 * explanation rather than a button that silently does nothing.
 */
export function VoiceActionButton({ capabilitiesState, voiceEnabled }: VoiceActionButtonProps) {
  if (capabilitiesState === 'loading') {
    return (
      <div>
        <Button variant="secondary" size="lg" disabled>
          Record by voice
        </Button>
        <p className="mt-1 text-xs text-ink-muted">Checking whether voice is available…</p>
      </div>
    );
  }

  if (capabilitiesState === 'error') {
    return (
      <div>
        <Button variant="secondary" size="lg" disabled>
          Record by voice
        </Button>
        <p className="mt-1 text-xs text-ink-muted">
          Could not check whether voice is available. Typing a record still works.
        </p>
      </div>
    );
  }

  if (!voiceEnabled) {
    return (
      <div>
        <Button variant="secondary" size="lg" disabled>
          Record by voice
        </Button>
        <p className="mt-1 text-xs text-ink-muted">
          Voice entry is not available yet. Planned for {PLANNED_FEATURES.voice.phase}.
        </p>
      </div>
    );
  }

  return (
    <Link to={notBuiltPath('voice')}>
      <Button variant="secondary" size="lg">
        Record by voice
      </Button>
    </Link>
  );
}
