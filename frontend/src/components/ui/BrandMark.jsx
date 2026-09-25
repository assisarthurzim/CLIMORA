import { Link } from 'react-router-dom';
import { Icon } from '@/components/ui/Icon';
import { APP_NAME, ROUTES } from '@/utils/constants';

export function BrandMark({ to = ROUTES.LANDING }) {
  return (
    <Link to={to} className="d-flex align-items-center gap-2 text-decoration-none">
      <span
        className="d-inline-flex align-items-center justify-content-center"
        style={{
          width: 32,
          height: 32,
          borderRadius: 'var(--radius-sm)',
          background: 'var(--accent)',
          color: 'var(--accent-content)',
        }}
      >
        <Icon name="cloud-sun" size={18} strokeWidth={2} />
      </span>
      <span
        className="type-display"
        style={{
          fontSize: 'var(--text-md)',
          fontWeight: 'var(--weight-semibold)',
          color: 'var(--content-primary)',
        }}
      >
        {APP_NAME}
      </span>
    </Link>
  );
}
