import { Link } from 'react-router-dom';

import { PageHeader } from '../app/PageHeader';
import { notBuiltPath } from '../app/plannedFeatures';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { InlineNotice } from '../components/ui/InlineNotice';
import { LoadingState } from '../components/ui/LoadingState';
import { SummaryStat } from '../components/ui/SummaryStat';
import { useCapabilities } from '../features/capabilities/useCapabilities';
import { VoiceActionButton } from '../features/voice-entry/VoiceActionButton';

export function WorkerHomePage() {
  const { state, data, error, reload } = useCapabilities();
  const voiceEnabled = state === 'ready' && data?.voice_enabled === true;

  return (
    <>
      <PageHeader
        title="Your work and pay"
        description="Days worked, wages agreed and payments you have received."
      />

      <div className="space-y-4">
        <Card title="Balance">
          <SummaryStat
            label="Outstanding amount"
            value="—"
            hint="No entries to calculate from yet"
          />
          <p className="mt-4 text-xs text-ink-muted">
            This figure will be calculated by the server from the entries you can open and inspect.
            MehnatLedger never shows an amount it cannot explain.
          </p>
          <div className="mt-4">
            <InlineNotice tone="info" title="Recording is not built yet" showToneLabel={false}>
              Work records, advances and payments arrive in Phase 3. Until then no balance is
              calculated.
            </InlineNotice>
          </div>
        </Card>

        <Card title="Record something">
          <div className="flex flex-wrap items-start gap-3">
            <Link to={notBuiltPath('addWorkRecord')}>
              <Button size="lg">Add work day</Button>
            </Link>
            <Link to={notBuiltPath('addPayment')}>
              <Button variant="secondary" size="lg">
                Add payment or advance
              </Button>
            </Link>
            <VoiceActionButton capabilitiesState={state} voiceEnabled={voiceEnabled} />
          </div>
        </Card>

        <Card title="Shared records from a business">
          <EmptyState
            title="Nothing shared with you yet"
            description="A business can share a work or payment record only if you have both accepted a link."
            action={
              <Link to="/shared">
                <Button variant="secondary" size="sm">
                  About Shared Hisaab
                </Button>
              </Link>
            }
          />
        </Card>

        <Card title="Recent work and payments">
          {state === 'loading' ? <LoadingState message="Loading recent records…" /> : null}
          {state === 'error' ? (
            <ErrorState message={error ?? 'Could not load recent records.'} onRetry={reload} />
          ) : null}
          {state === 'ready' ? (
            <EmptyState
              title="No work or payment records yet"
              description="Records will appear here after you add your first work day or payment."
            />
          ) : null}
        </Card>
      </div>
    </>
  );
}
