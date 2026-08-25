import type { ReactNode } from 'react';
import styles from './Field.module.css';

export function Field({
  label,
  hint,
  htmlFor,
  children,
}: {
  label: string;
  hint?: string;
  htmlFor?: string;
  children: ReactNode;
}) {
  return (
    <div className={styles.field}>
      <label className={styles.fieldLabel} htmlFor={htmlFor}>
        {label}
      </label>
      {children}
      {hint && <p className={styles.fieldHint}>{hint}</p>}
    </div>
  );
}
