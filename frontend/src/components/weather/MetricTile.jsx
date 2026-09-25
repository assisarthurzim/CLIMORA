import { Icon } from '@/components/ui/Icon';

export function MetricTile({ icon, label, value, hint }) {
  return (
    <div className="surface climora-tile h-100 p-3 d-flex flex-column gap-2">
      <div className="d-flex align-items-center gap-2" style={{ color: 'var(--content-muted)' }}>
        <Icon name={icon} size={14} />
        <span className="type-label">{label}</span>
      </div>
      <span className="type-numeric" style={{ fontSize: 'var(--text-xl)', lineHeight: 1.1 }}>
        {value}
      </span>
      {hint ? (
        <span className="mt-auto" style={{ fontSize: 'var(--text-xs)', color: 'var(--content-secondary)' }}>
          {hint}
        </span>
      ) : null}
    </div>
  );
}
