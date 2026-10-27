import { useCallback, useEffect, useState } from 'react';

import { api } from '../../services/api/client';
import type { Capabilities } from '../../services/api/types';

export type AsyncState = 'loading' | 'ready' | 'error';

interface CapabilitiesResult {
  state: AsyncState;
  data: Capabilities | null;
  error: string | null;
  reload: () => void;
}

/**
 * Load the server's capability report.
 *
 * The server is the source of truth for whether voice features exist. This
 * hook never guesses: an unreachable server surfaces an error state rather
 * than assuming anything is available.
 */
export function useCapabilities(): CapabilitiesResult {
  const [state, setState] = useState<AsyncState>('loading');
  const [data, setData] = useState<Capabilities | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  const reload = useCallback(() => {
    setReloadToken((token) => token + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setState('loading');
    setError(null);

    api
      .getCapabilities()
      .then((capabilities) => {
        if (cancelled) return;
        setData(capabilities);
        setState('ready');
      })
      .catch((cause: unknown) => {
        if (cancelled) return;
        setData(null);
        setError(cause instanceof Error ? cause.message : 'Something went wrong.');
        setState('error');
      });

    return () => {
      cancelled = true;
    };
  }, [reloadToken]);

  return { state, data, error, reload };
}
