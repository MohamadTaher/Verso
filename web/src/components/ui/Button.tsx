import type { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from 'react';
import styles from './Button.module.css';

type Variant = 'primary' | 'secondary' | 'quiet' | 'danger';
type Size = 'lg' | 'md' | 'sm';

const buttonClass = (variant: Variant, size: Size, className?: string) =>
  [styles.button, styles[variant], styles[size], className].filter(Boolean).join(' ');

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
};

export function Button({
  variant = 'secondary',
  size = 'md',
  icon,
  iconPosition = 'left',
  className,
  children,
  ...rest
}: ButtonProps) {
  return (
    <button className={buttonClass(variant, size, className)} {...rest}>
      {icon && iconPosition === 'left' && (
        <span className={styles.buttonIcon} aria-hidden="true">
          {icon}
        </span>
      )}
      <span className={styles.buttonText}>{children}</span>
      {icon && iconPosition === 'right' && (
        <span className={styles.buttonIcon} aria-hidden="true">
          {icon}
        </span>
      )}
    </button>
  );
}

type LinkButtonProps = AnchorHTMLAttributes<HTMLAnchorElement> & {
  variant?: Extract<Variant, 'primary' | 'secondary'>;
  size?: Size;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
};

export function LinkButton({
  variant = 'secondary',
  size = 'md',
  icon,
  iconPosition = 'left',
  className,
  children,
  ...rest
}: LinkButtonProps) {
  return (
    <a className={buttonClass(variant, size, className)} {...rest}>
      {icon && iconPosition === 'left' && (
        <span className={styles.buttonIcon} aria-hidden="true">
          {icon}
        </span>
      )}
      <span className={styles.buttonText}>{children}</span>
      {icon && iconPosition === 'right' && (
        <span className={styles.buttonIcon} aria-hidden="true">
          {icon}
        </span>
      )}
    </a>
  );
}
