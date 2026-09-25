import { Icon } from '@/components/ui/Icon';

/**
 * Empty and error states share one shape: say what happened, then offer the
 * next move. A blank panel is a dead end.
 */
export function StateMessage({ icon = 'info', title, description, action }) {
  return (
    <div className="text-center py-5 px-3">
      <span
        className="d-inline-flex align-items-center justify-content-center mb-3"
        style={{
          width: 52,
          height: 52,
          borderRadius: 'var(--radius-lg)',
          background: 'var(--surface-sunken)',
          color: 'var(--content-muted)',
        }}
      >
        <Icon name={icon} size={22} />
      </span>
      <h2 className="h5 fw-medium mb-2">{title}</h2>
      {description ? (
        <p className="mb-4 mx-auto" style={{ maxWidth: 420, color: 'var(--content-secondary)' }}>
          {description}
        </p>
      ) : null}
      {action}
    </div>
  );
}
