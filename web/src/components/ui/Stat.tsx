import type { ReactNode } from 'react';
import styles from './Stat.module.css';

export function Stat({
  value,
  label,
  subtext,
  icon,
}: {
  value: ReactNode;
  label: string;
  subtext?: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <div className={styles.stat}>
      <div className={styles.statHeader}>
        <span className={styles.statLabel}>{label}</span>
        {icon && <span className={styles.statIcon} aria-hidden="true">{icon}</span>}
      </div>
      <span className={styles.statValue}>{value}</span>
      {subtext && <span className={styles.statSubtext}>{subtext}</span>}
    </div>
  );
}
