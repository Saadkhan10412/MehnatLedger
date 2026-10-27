import { useNavigate } from 'react-router-dom';

import { Button } from '../components/ui/Button';
import { InlineNotice } from '../components/ui/InlineNotice';
import { modeHomePath, useMode, type AppMode } from '../features/mode/ModeContext';

interface ModeOption {
  mode: AppMode;
  title: string;
  description: string;
  examples: string[];
}

const OPTIONS: ModeOption[] = [
  {
    mode: 'business',
    title: 'Business',
    description: 'For shopkeepers and small business owners.',
    examples: ['Record daily sales and expenses', 'Keep wage and payment records for workers'],
  },
  {
    mode: 'worker',
    title: 'Worker',
    description: 'For daily-wage and informal workers.',
    examples: ['Record days or shifts worked', 'Track advances and payments received'],
  },
];

export function ChooseModePage() {
  const { setMode } = useMode();
  const navigate = useNavigate();

  const choose = (mode: AppMode) => {
    setMode(mode);
    navigate(modeHomePath(mode));
  };

  return (
    <div className="min-h-dvh bg-surface">
      <div className="mx-auto w-full max-w-2xl px-4 py-8 sm:py-12">
        <p className="text-2xl font-semibold text-ink">
          Mehnat<span className="text-primary-strong">Ledger</span>
        </p>
        <h1 className="mt-6 text-xl font-semibold text-ink sm:text-2xl">How will you use it?</h1>
        <p className="mt-1 text-sm text-ink-muted">
          You can change this later. This choice is only stored on this device for now.
        </p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {OPTIONS.map((option) => (
            <div
              key={option.mode}
              className="flex flex-col rounded-[var(--radius-card)] border border-line bg-surface-raised p-4"
            >
              <h2 className="text-lg font-semibold text-ink">{option.title}</h2>
              <p className="mt-1 text-sm text-ink-muted">{option.description}</p>
              <ul className="mt-3 flex-1 space-y-1 text-sm text-ink">
                {option.examples.map((example) => (
                  <li key={example} className="flex gap-2">
                    <span aria-hidden="true" className="text-primary-strong">
                      •
                    </span>
                    <span>{example}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-4">
                <Button fullWidth onClick={() => choose(option.mode)}>
                  Continue as {option.title.toLowerCase()}
                </Button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6">
          <InlineNotice tone="info" title="Preview build">
            Recording, sharing and voice features are being built in stages. Nothing you do here
            saves bookkeeping records yet.
          </InlineNotice>
        </div>
      </div>
    </div>
  );
}
