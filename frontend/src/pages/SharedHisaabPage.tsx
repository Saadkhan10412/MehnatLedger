import { Link } from 'react-router-dom';

import { PageHeader } from '../app/PageHeader';
import { notBuiltPath } from '../app/plannedFeatures';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';
import { InlineNotice } from '../components/ui/InlineNotice';

const STATUS_LABELS = [
  {
    label: 'Proposed',
    meaning: 'One side recorded it and it is waiting for the other side to look at it.',
  },
  {
    label: 'Acknowledged',
    meaning: 'The other side confirmed the details as shown. This is not a legal guarantee.',
  },
  {
    label: 'Disputed',
    meaning: 'Someone questioned the record. The disagreement stays visible until it is resolved.',
  },
  {
    label: 'Paid / Settled',
    meaning: 'Only shown when a payment event was actually recorded, never inferred from a reply.',
  },
];

export function SharedHisaabPage() {
  return (
    <>
      <PageHeader
        title="Shared Hisaab"
        description="Records a business and a worker have both agreed to share."
      />

      <div className="space-y-4">
        <Card>
          <EmptyState
            title="No linked accounts yet"
            description="Linking is opt-in. Both people must accept before either can see a shared record, and linking never exposes your other private entries."
          />
        </Card>

        <Card
          title="How linking will work"
          description="Planned for Phase 4 — Shared Hisaab and dispute workflow."
        >
          <ol className="space-y-3 text-sm text-ink">
            <li className="flex gap-3">
              <span className="font-semibold text-primary-strong">1</span>
              <span>One side sends an invitation to link accounts.</span>
            </li>
            <li className="flex gap-3">
              <span className="font-semibold text-primary-strong">2</span>
              <span>The other side accepts. Until they do, nothing is shared.</span>
            </li>
            <li className="flex gap-3">
              <span className="font-semibold text-primary-strong">3</span>
              <span>Only the specific records in the agreed scope are visible to both sides.</span>
            </li>
            <li className="flex gap-3">
              <span className="font-semibold text-primary-strong">4</span>
              <span>Either side can stop sharing later, and the existing history is kept.</span>
            </li>
          </ol>
          <div className="mt-4">
            <Link to={notBuiltPath('linkAccount')}>
              <Button variant="secondary" size="sm">
                Details
              </Button>
            </Link>
          </div>
        </Card>

        <Card title="What the labels mean">
          <dl className="space-y-3">
            {STATUS_LABELS.map((status) => (
              <div key={status.label}>
                <dt className="text-sm font-semibold text-ink">{status.label}</dt>
                <dd className="text-sm text-ink-muted">{status.meaning}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-4 text-xs text-ink-muted">
            These are label definitions, not records. No shared records exist yet.
          </p>
        </Card>

        <InlineNotice tone="warning" title="Nothing here is shared or saved">
          Invitations, acknowledgements and disputes are not implemented yet, so this screen cannot
          change any record.
        </InlineNotice>
      </div>
    </>
  );
}
