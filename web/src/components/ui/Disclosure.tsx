import type { ReactNode } from 'react';
import styles from './Disclosure.module.css';

export function Disclosure({
  summary,
  children,
  badge,
  defaultOpen = false,
}: {
  summary: ReactNode;
  children: ReactNode;
  badge?: ReactNode;
  defaultOpen?: boolean;
}) {
  return (
    <details className={styles.disclosure} open={defaultOpen}>
      <summary className={styles.disclosureSummary}>
        <span className={styles.summaryTitle}>{summary}</span>
        {badge && <span className={styles.summaryBadge}>{badge}</span>}
      </summary>
      <div className={styles.disclosureBody}>{children}</div>
    </details>
  );
}
