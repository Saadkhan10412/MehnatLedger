import { Link } from 'react-router-dom';

import { Button } from '../components/ui/Button';
import { PageHeader } from '../app/PageHeader';
import { modeHomePath, useMode } from '../features/mode/ModeContext';

export function NotFoundPage() {
  const { mode } = useMode();
  const home = mode ? modeHomePath(mode) : '/';

  return (
    <>
      <PageHeader title="Page not found" description="That address does not exist in this app." />
      <Link to={home}>
        <Button variant="secondary">Go to home</Button>
      </Link>
    </>
  );
}
