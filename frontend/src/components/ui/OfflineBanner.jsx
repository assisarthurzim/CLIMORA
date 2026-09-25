import { Icon } from '@/components/ui/Icon';
import { useOnlineStatus } from '@/hooks/useOnlineStatus';

export function OfflineBanner() {
  const isOnline = useOnlineStatus();

  if (isOnline) return null;

  return (
    <div
      className="d-flex align-items-center justify-content-center gap-2 py-2 px-3 small"
      style={{ background: 'var(--warning-quiet)', color: 'var(--warning)' }}
      role="alert"
    >
      <Icon name="offline" size={14} />
      Sem conexão. Os dados na tela podem estar desatualizados.
    </div>
  );
}
