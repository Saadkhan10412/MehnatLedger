import { Link, Outlet } from 'react-router-dom';

import { useMode } from '../features/mode/ModeContext';
import { ModeSwitcher } from './ModeSwitcher';
import { PrimaryNavigation } from './PrimaryNavigation';

export function AppShell() {
  const { mode } = useMode();

  // A mode is always chosen before the shell renders (see App route gate).
  if (!mode) {
    return null;
  }

  return (
    <div className="min-h-dvh bg-surface">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-surface-raised focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-ink focus:shadow"
      >
        Skip to content
      </a>

      <header className="border-b border-line bg-surface-raised">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between gap-3 px-4 py-3">
          <Link to={mode === 'business' ? '/business' : '/worker'} className="text-lg font-semibold text-ink">
            Mehnat<span className="text-primary-strong">Ledger</span>
          </Link>
          <ModeSwitcher />
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-5xl gap-6 px-4">
        <div className="hidden py-6 lg:block">
          <PrimaryNavigation mode={mode} variant="sidebar" />
        </div>

        <main id="main-content" className="min-w-0 flex-1 pb-24 pt-5 lg:pb-8">
          <Outlet />
          <footer className="mt-10 border-t border-line pt-4 text-xs text-ink-muted">
            <p>
              Preview build. Business and worker ledger records are not implemented yet; screens
              marked with a phase are placeholders and do not save data.
            </p>
          </footer>
        </main>
      </div>

      <PrimaryNavigation mode={mode} variant="bottom" />
    </div>
  );
}
