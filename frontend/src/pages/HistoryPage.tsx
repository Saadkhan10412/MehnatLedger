import { Link } from 'react-router-dom';

import { PageHeader } from '../app/PageHeader';
import { notBuiltPath } from '../app/plannedFeatures';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { EmptyState } from '../components/ui/EmptyState';
import { InlineNotice } from '../components/ui/InlineNotice';
import { modeHomePath, useMode } from '../features/mode/ModeContext';

export function HistoryPage() {
  const { mode } = useMode();

  return (
    <>
      <PageHeader
        title="History"
        description="Every record you have created, in date order."
      />

      <div className="space-y-4">
        <Card>
          <EmptyState
            title="No records yet"
            description="Your history will appear here after you record your first entry. There are no sample records in this app."
            action={
              <Link to={mode ? modeHomePath(mode) : '/'}>
                <Button variant="secondary" size="sm">
                  Go to home
                </Button>
              </Link>
            }
          />
        </Card>

        <InlineNotice tone="info" title="Filters arrive with the ledger">
          Date and type filters, plus CSV export, are planned for Phase 3. Controls that do nothing
          are deliberately not shown.
        </InlineNotice>

        <div>
          <Link to={notBuiltPath('export')}>
            <Button variant="quiet" size="sm">
              About export
            </Button>
          </Link>
        </div>
      </div>
    </>
  );
}
