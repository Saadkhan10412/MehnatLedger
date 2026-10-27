export type ButtonVariant = 'primary' | 'secondary' | 'quiet' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

const BASE =
  'inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-colors ' +
  'disabled:cursor-not-allowed disabled:opacity-60';

// Every size keeps a minimum 44px touch target (design.md section 8).
const VARIANTS: Record<ButtonVariant, string> = {
  primary: 'bg-primary text-white hover:bg-primary-strong',
  secondary: 'bg-surface-raised text-ink border border-line-strong hover:bg-primary-soft',
  quiet: 'text-secondary hover:bg-secondary-soft',
  danger: 'bg-danger text-white hover:brightness-90',
};

const SIZES: Record<ButtonSize, string> = {
  sm: 'min-h-11 px-3 text-sm',
  md: 'min-h-11 px-4 text-sm',
  lg: 'min-h-12 px-5 text-base',
};

export function buttonClasses(variant: ButtonVariant = 'primary', size: ButtonSize = 'md'): string {
  return `${BASE} ${VARIANTS[variant]} ${SIZES[size]}`;
}
