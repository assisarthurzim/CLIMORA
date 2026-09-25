import { Icon } from '@/components/ui/Icon';

export function AlertMessage({ message, tone = 'error' }) {
  if (!message) return null;

  const color = tone === 'error' ? 'var(--danger)' : 'var(--warning)';
  const background = tone === 'error' ? 'var(--danger-quiet)' : 'var(--warning-quiet)';

  return (
    <div
      role="alert"
      className="d-flex align-items-start gap-2 p-3 mb-3 small"
      style={{ borderRadius: 'var(--radius-md)', background, color }}
    >
      <span style={{ lineHeight: 0, marginTop: 1 }}>
        <Icon name={tone === 'error' ? 'error' : 'warning'} size={16} />
      </span>
      <span style={{ lineHeight: 'var(--leading-snug)' }}>{message}</span>
    </div>
  );
}
