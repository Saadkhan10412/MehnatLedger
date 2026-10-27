import { ModeSwitcher } from '../app/ModeSwitcher';
import { PageHeader } from '../app/PageHeader';
import { Card } from '../components/ui/Card';
import { ErrorState } from '../components/ui/ErrorState';
import { InlineNotice } from '../components/ui/InlineNotice';
import { LoadingState } from '../components/ui/LoadingState';
import { useCapabilities } from '../features/capabilities/useCapabilities';
import type { ProviderCapability } from '../services/api/types';

/** Renders capability state in plain words, never overstating readiness. */
function ProviderRow({ title, capability }: { title: string; capability: ProviderCapability }) {
  const summary = capability.api_key_configured
    ? 'A credential is configured, but this integration has not been verified.'
    : 'Not configured. This feature cannot run yet.';

  return (
    <div className="border-b border-line pb-3 last:border-b-0 last:pb-0">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-semibold text-ink">{title}</p>
        <span className="rounded-full bg-secondary-soft px-2.5 py-0.5 text-xs font-medium text-secondary-strong">
          {capability.mode}
        </span>
      </div>
      <p className="mt-1 text-sm text-ink-muted">{summary}</p>
    </div>
  );
}

export function SettingsPage() {
  const { state, data, error, reload } = useCapabilities();

  return (
    <>
      <PageHeader title="Settings" description="Mode, language, and what this app can do right now." />

      <div className="space-y-4">
        <Card title="Mode" description="Which experience you are using.">
          <ModeSwitcher />
          <p className="mt-3 text-xs text-ink-muted">
            This choice is stored on this device only. Accounts do not exist yet (Phase 2), so it is
            not yet tied to a profile.
          </p>
        </Card>

        <Card title="Language">
          <p className="text-sm text-ink">
            <span className="font-semibold">Interface:</span> English
          </p>
          <p className="mt-2 text-sm text-ink-muted">
            Indian-language labels and speech will be enabled one at a time, and only after the voice
            pipeline has actually been tested for that language. No language is claimed as supported
            yet.
          </p>
        </Card>

        <Card title="Voice and AI status" description="Reported by the server, not assumed by this app.">
          {state === 'loading' ? <LoadingState message="Checking server capabilities…" /> : null}
          {state === 'error' ? (
            <ErrorState message={error ?? 'Could not load capability status.'} onRetry={reload} />
          ) : null}
          {state === 'ready' && data ? (
            <div className="space-y-3">
              <ProviderRow title="Speech to text (speech recognition)" capability={data.speech_to_text} />
              <ProviderRow title="Text to speech (read aloud)" capability={data.text_to_speech} />
              <ProviderRow title="Reasoning and field extraction" capability={data.reasoning} />
              <p className="pt-1 text-sm text-ink">
                <span className="font-semibold">Voice entry: </span>
                {data.voice_enabled ? 'available' : 'not available'}
              </p>
              <p className="text-sm text-ink">
                <span className="font-semibold">Typing records by hand: </span>
                {data.manual_entry_available ? 'available' : 'unavailable'}
              </p>
            </div>
          ) : null}
        </Card>

        <Card title="Server" description="The backend this app is talking to.">
          {state === 'ready' && data ? (
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-ink-muted">Service</dt>
                <dd className="text-right font-medium text-ink">{data.service}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-ink-muted">Environment</dt>
                <dd className="text-right font-medium text-ink">{data.environment}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-ink-muted">Audio limit per voice clip</dt>
                <dd className="text-right font-medium text-ink">{data.voice_max_audio_seconds} seconds</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-ink-muted">Voice drafts per day</dt>
                <dd className="text-right font-medium text-ink">{data.voice_daily_drafts_per_user}</dd>
              </div>
            </dl>
          ) : (
            <p className="text-sm text-ink-muted">
              Server details appear once the capability check succeeds.
            </p>
          )}
        </Card>

        <Card title="Privacy">
          <ul className="space-y-2 text-sm text-ink-muted">
            <li>Only the profile details needed for the service will be collected.</li>
            <li>Your records are not used to train AI models by default.</li>
            <li>
              Provider credentials are held on the server only and are never sent to this browser.
              There is no way to enter an API key in this app, by design.
            </li>
            <li>Voice audio will be sent to the server only when you start recording.</li>
          </ul>
        </Card>

        <InlineNotice tone="info" title="Accounts are not available yet">
          Signing in, saving records and linking accounts arrive in later phases. Nothing in this
          preview writes bookkeeping data.
        </InlineNotice>
      </div>
    </>
  );
}
