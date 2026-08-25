import styles from './Meter.module.css';

/**
 * A labelled progress bar with optional shimmer/active state.
 */
export function Meter({
  value,
  max,
  over = false,
  animated = false,
}: {
  value: number;
  max: number;
  over?: boolean;
  animated?: boolean;
}) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div
      className={`${styles.meter} ${over ? styles.meterOver : ''} ${animated ? styles.meterAnimated : ''}`}
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={max}
    >
      <div className={styles.meterFill} style={{ width: `${pct}%` }} />
    </div>
  );
}
