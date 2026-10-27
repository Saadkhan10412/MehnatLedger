import type { Capabilities, Health } from './types';

/**
 * Small typed API client.
 *
 * `VITE_API_BASE_URL` is a build-time, browser-visible value and therefore must
 * never hold a secret. It is empty by default, which makes requests same-origin
 * and lets the Vite dev proxy reach the backend.
 */
const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? '';
const DEFAULT_TIMEOUT_MS = 8000;

export class ApiError extends Error {
  readonly status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(path: string, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<T> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new ApiError(`The server returned an error (status ${response.status}).`, response.status);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('The server took too long to respond.');
    }
    throw new ApiError('Could not reach the server. Check that the backend is running.');
  } finally {
    window.clearTimeout(timer);
  }
}

export const api = {
  getHealth: (): Promise<Health> => request<Health>('/api/v1/health'),
  getCapabilities: (): Promise<Capabilities> => request<Capabilities>('/api/v1/system/capabilities'),
};
