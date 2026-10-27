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

export function BusinessHomePage() {
  const { state, data, error, reload } = useCapabilities();
  const voiceEnabled = state === 'ready' && data?.voice_enabled === true;

  return (
    <>
      <PageHeader
        title="Today"
        description="Your shop's records for today: sales, expenses and worker payments."
      />

      <div className="space-y-4">
        <Card title="Today's totals">
          <div className="grid grid-cols-2 gap-4">
            <SummaryStat label="Sales" value="—" hint="Nothing recorded yet" />
            <SummaryStat label="Expenses" value="—" hint="Nothing recorded yet" />
          </div>
          <p className="mt-4 text-xs text-ink-muted">
            Totals will be calculated by the server from your own entries. They are never estimated
            on the device.
          </p>
          <div className="mt-4">
            <InlineNotice tone="info" title="Recording is not built yet" showToneLabel={false}>
              Adding sales and expenses arrives in Phase 3. Until then these totals stay empty.
            </InlineNotice>
          </div>
        </Card>

        <Card title="Record something">
          <div className="flex flex-wrap items-start gap-3">
            <Link to={notBuiltPath('addSale')}>
              <Button size="lg">Add sale</Button>
            </Link>
            <Link to={notBuiltPath('addExpense')}>
              <Button variant="secondary" size="lg">
                Add expense
              </Button>
            </Link>
            <VoiceActionButton capabilitiesState={state} voiceEnabled={voiceEnabled} />
          </div>
        </Card>

        <Card title="Shared records needing review" description="Records a linked worker has proposed.">
          <EmptyState
            title="No shared records yet"
            description="You will see a record here only after you link a worker account and they share something with you."
            action={
              <Link to="/shared">
                <Button variant="secondary" size="sm">
                  About Shared Hisaab
                </Button>
              </Link>
            }
          />
        </Card>

        <Card title="Recent activity">
          {state === 'loading' ? <LoadingState message="Loading recent activity…" /> : null}
          {state === 'error' ? (
            <ErrorState message={error ?? 'Could not load recent activity.'} onRetry={reload} />
          ) : null}
          {state === 'ready' ? (
            <EmptyState
              title="No entries recorded yet"
              description="Your ledger will appear here after you record your first sale or expense."
            />
          ) : null}
        </Card>
      </div>
    </>
  );
}
