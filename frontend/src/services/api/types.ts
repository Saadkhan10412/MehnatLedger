/**
 * Types mirroring the backend's Pydantic response schemas.
 * Keep these in sync with `backend/app/schemas/system.py`.
 */

export type ProviderMode = 'disabled' | 'mock' | 'local' | 'live';

export interface ProviderCapability {
  provider: string;
  mode: ProviderMode;
  /** True only when a credential string was supplied -- NOT proof it works. */
  api_key_configured: boolean;
  base_url_configured: boolean;
  integration_verified: boolean;
}

export interface Capabilities {
  service: string;
  environment: string;
  speech_to_text: ProviderCapability;
  text_to_speech: ProviderCapability;
  reasoning: ProviderCapability;
  voice_enabled: boolean;
  manual_entry_available: boolean;
  voice_max_audio_seconds: number;
  voice_daily_drafts_per_user: number;
  server_time: string;
}

export interface Health {
  status: 'ok';
  service: string;
  environment: string;
  api_version: string;
}
