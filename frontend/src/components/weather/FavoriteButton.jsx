import { useState } from 'react';
import { Icon } from '@/components/ui/Icon';

export function FavoriteButton({ favorite, onAdd, onRemove }) {
  const [isBusy, setIsBusy] = useState(false);
  const isFavorite = Boolean(favorite);

  async function handleClick() {
    setIsBusy(true);
    try {
      await (isFavorite ? onRemove(favorite.id) : onAdd());
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <button
      type="button"
      className="btn-climora d-flex align-items-center justify-content-center"
      style={{
        width: 38,
        height: 38,
        padding: 0,
        borderRadius: '50%',
        background: isFavorite ? 'var(--warning-quiet)' : 'var(--surface-sunken)',
      }}
      onClick={handleClick}
      disabled={isBusy}
      aria-pressed={isFavorite}
      aria-label={isFavorite ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
      title={isFavorite ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
    >
      <Icon
        name="star"
        size={17}
        strokeWidth={isFavorite ? 2 : 1.75}
        style={{
          color: isFavorite ? 'var(--warning)' : 'var(--content-muted)',
          fill: isFavorite ? 'var(--warning)' : 'none',
        }}
      />
    </button>
  );
}
