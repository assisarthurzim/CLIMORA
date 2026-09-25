import { Icon } from '@/components/ui/Icon';
import { IconButton } from '@/components/ui/Button';
import { useToast } from '@/context/ToastContext';

const TONES = {
  info: { icon: 'info', color: 'var(--accent)' },
  success: { icon: 'check', color: 'var(--positive)' },
  warning: { icon: 'warning', color: 'var(--warning)' },
  error: { icon: 'error', color: 'var(--danger)' },
};

export function ToastStack() {
  const { toasts, dismiss } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div
      className="position-fixed d-flex flex-column gap-2 climora-toast-stack"
      style={{ bottom: 24, right: 24, zIndex: 1100, maxWidth: 400 }}
      role="status"
      aria-live="polite"
    >
      {toasts.map((toast) => {
        const tone = TONES[toast.tone] ?? TONES.info;
        return (
          <div
            key={toast.id}
            className="glass-surface climora-toast d-flex align-items-start gap-3 p-3"
          >
            <span style={{ color: tone.color, lineHeight: 0, marginTop: 2 }}>
              <Icon name={tone.icon} size={17} />
            </span>
            <span className="small flex-grow-1" style={{ lineHeight: 'var(--leading-snug)' }}>
              {toast.message}
            </span>
            <IconButton name="close" label="Fechar aviso" size={14} onClick={() => dismiss(toast.id)} />
          </div>
        );
      })}
    </div>
  );
}
