import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';

export type AppMode = 'business' | 'worker';

/**
 * TEMPORARY Phase 1 placeholder.
 *
 * Accounts do not exist yet (Phase 2), so the chosen mode is stored as a
 * device-level preference. Once users have profiles, the mode must come from
 * the account instead, and this storage key should be removed.
 *
 * Whether one account may hold both Business and Worker modes is an open
 * product question (prd.md section 10) and is NOT decided here.
 */
const STORAGE_KEY = 'mehnatledger.shell.mode';

interface ModeContextValue {
  mode: AppMode | null;
  hasChosenMode: boolean;
  setMode: (mode: AppMode) => void;
  clearMode: () => void;
}

const ModeContext = createContext<ModeContextValue | null>(null);

export function isAppMode(value: unknown): value is AppMode {
  return value === 'business' || value === 'worker';
}

function readStoredMode(): AppMode | null {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return isAppMode(stored) ? stored : null;
  } catch {
    // Storage can be unavailable (private mode, blocked cookies).
    return null;
  }
}

export function ModeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<AppMode | null>(readStoredMode);

  const setMode = useCallback((next: AppMode) => {
    setModeState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Non-fatal: the choice simply will not persist across sessions.
    }
  }, []);

  const clearMode = useCallback(() => {
    setModeState(null);
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Non-fatal.
    }
  }, []);

  const value = useMemo<ModeContextValue>(
    () => ({ mode, hasChosenMode: mode !== null, setMode, clearMode }),
    [mode, setMode, clearMode],
  );

  return <ModeContext.Provider value={value}>{children}</ModeContext.Provider>;
}

export function useMode(): ModeContextValue {
  const context = useContext(ModeContext);
  if (!context) {
    throw new Error('useMode must be used inside a ModeProvider.');
  }
  return context;
}

export const modeHomePath = (mode: AppMode): string => (mode === 'business' ? '/business' : '/worker');

export const MODE_LABELS: Record<AppMode, string> = {
  business: 'Business',
  worker: 'Worker',
};
