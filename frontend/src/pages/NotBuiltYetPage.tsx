import { Link, useSearchParams } from 'react-router-dom';

import { PageHeader } from '../app/PageHeader';
import { Button } from '../components/ui/Button';
import { InlineNotice } from '../components/ui/InlineNotice';
import { PLANNED_FEATURES } from '../app/plannedFeatures';

const DEFAULT_FEATURE = PLANNED_FEATURES.addSale;

export function NotBuiltYetPage() {
  const [params] = useSearchParams();
  const feature = params.get('feature') ?? DEFAULT_FEATURE.feature;
  const phase = params.get('phase') ?? DEFAULT_FEATURE.phase;

  return (
    <>
      <PageHeader
        title="Not built yet"
        description="This part of MehnatLedger has not been implemented, so nothing was saved."
      />

      <div className="space-y-4">
        <div className="rounded-[var(--radius-card)] border border-line bg-surface-raised p-4">
          <p className="text-sm text-ink">
            <span className="font-semibold">You asked for:</span> {feature}
          </p>
          <p className="mt-2 text-sm text-ink-muted">
            <span className="font-semibold text-ink">Planned for:</span> {phase}
          </p>
        </div>

        <InlineNotice tone="warning" title="No data was recorded">
          This screen is a placeholder. MehnatLedger does not create sample or demo ledger entries,
          so nothing has been written to your books.
        </InlineNotice>

        <div>
          <Link to="/settings">
            <Button variant="secondary">Check what is available</Button>
          </Link>
        </div>
      </div>
    </>
  );
}
