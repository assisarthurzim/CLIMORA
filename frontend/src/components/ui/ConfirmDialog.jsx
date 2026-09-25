import { useState } from 'react';
import { Button } from '@/components/ui/Button';

export function ConfirmDialog({
  title,
  description,
  confirmLabel,
  isDestructive = false,
  requiresText,
  onConfirm,
  onCancel,
}) {
  const [typed, setTyped] = useState('');
  const [isBusy, setIsBusy] = useState(false);

  // A destructive action that only needs one click is a destructive action
  // waiting to happen by accident.
  const canConfirm = !requiresText || typed === requiresText;

  async function handleConfirm() {
    setIsBusy(true);
    try {
      await onConfirm();
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <div className="climora-scrim" role="dialog" aria-modal="true">
      <div className="climora-dialog">
        <h2 className="h5 fw-semibold mb-2">{title}</h2>
        <p className="mb-3" style={{ color: 'var(--content-secondary)' }}>
          {description}
        </p>

        {requiresText ? (
          <div className="mb-3">
            <label className="form-label small">
              Digite <strong>{requiresText}</strong> para confirmar
            </label>
            <input
              type="text"
              className="form-control"
              value={typed}
              onChange={(event) => setTyped(event.target.value)}
              autoComplete="off"
            />
          </div>
        ) : null}

        <div className="d-flex justify-content-end gap-2">
          <Button variant="ghost" pill onClick={onCancel}>
            Cancelar
          </Button>
          <Button
            variant={isDestructive ? 'danger' : 'primary'}
            pill
            onClick={handleConfirm}
            disabled={!canConfirm}
            isLoading={isBusy}
            loadingLabel="Processando…"
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
