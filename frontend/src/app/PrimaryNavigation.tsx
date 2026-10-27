import { NavLink } from 'react-router-dom';

import { modeHomePath, type AppMode } from '../features/mode/ModeContext';

interface NavItem {
  to: string;
  label: string;
  end?: boolean;
}

/**
 * Single source of truth for navigation, shared by the desktop sidebar and the
 * mobile bottom bar so the two layouts never diverge in available features.
 */
export function navItemsFor(mode: AppMode): NavItem[] {
  return [
    { to: modeHomePath(mode), label: 'Home', end: true },
    { to: '/history', label: 'History' },
    { to: '/shared', label: 'Hisaab' },
    { to: '/settings', label: 'Settings' },
  ];
}

interface PrimaryNavigationProps {
  mode: AppMode;
  variant: 'sidebar' | 'bottom';
}

export function PrimaryNavigation({ mode, variant }: PrimaryNavigationProps) {
  const items = navItemsFor(mode);

  if (variant === 'sidebar') {
    return (
      <nav aria-label="Primary" className="w-44 shrink-0">
        <ul className="flex flex-col gap-1">
          {items.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex min-h-11 items-center rounded-lg px-3 text-sm font-medium transition-colors ${
                    isActive ? 'bg-primary-soft text-primary-strong' : 'text-ink-muted hover:bg-surface-raised'
                  }`
                }
              >
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    );
  }

  return (
    <nav
      aria-label="Primary"
      className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-surface-raised pb-[env(safe-area-inset-bottom)] lg:hidden"
    >
      <ul className="mx-auto flex max-w-3xl">
        {items.map((item) => (
          <li key={item.to} className="flex-1">
            <NavLink
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex min-h-14 flex-col items-center justify-center px-1 text-xs font-medium ${
                  isActive ? 'text-primary-strong' : 'text-ink-muted'
                }`
              }
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
