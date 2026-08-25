import type { ReactNode } from 'react';
import type { Notice, Tone } from '@/noticeMessages';
import styles from './Callout.module.css';

export function Callout({
  tone = 'info',
  title,
  children,
}: {
  tone?: Tone;
  title?: string;
  children: ReactNode;
}) {
  return (
    <div className={`${styles.callout} ${styles[`tone-${tone}`]}`} role={tone === 'error' ? 'alert' : undefined}>
      <div className={styles.calloutIcon} aria-hidden="true">
        {tone === 'error' && '✕'}
        {tone === 'warning' && '⚠'}
        {tone === 'success' && '✓'}
        {tone === 'info' && 'ℹ'}
      </div>
      <div className={styles.calloutContent}>
        {title && <p className={styles.calloutTitle}>{title}</p>}
        <div className={styles.calloutBody}>{children}</div>
      </div>
    </div>
  );
}

/** A Callout for one of the notices in `noticeMessages.ts`; nothing at all when there is none. */
export function NoticeCallout({ notice }: { notice: Notice | null }) {
  if (!notice) return null;
  return (
    <Callout tone={notice.tone} title={notice.title}>
      {notice.body}
    </Callout>
  );
}
