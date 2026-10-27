import type { ButtonHTMLAttributes } from 'react';

import { buttonClasses, type ButtonSize, type ButtonVariant } from './buttonStyles';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
}

export function Button({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  className = '',
  type = 'button',
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      className={[buttonClasses(variant, size), fullWidth ? 'w-full' : '', className]
        .filter(Boolean)
        .join(' ')}
      {...rest}
    />
  );
}
