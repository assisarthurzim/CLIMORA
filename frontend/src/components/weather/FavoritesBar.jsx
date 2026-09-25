import { buildLocationKey } from '@/utils/location';

export function FavoritesBar({ favorites, activeCoordinates, onSelect }) {
  if (favorites.length === 0) {
    return (
      <p className="small mb-0" style={{ color: 'var(--content-muted)' }}>
        Marque uma cidade com a estrela para acessá-la rapidamente aqui.
      </p>
    );
  }

  const activeKey = activeCoordinates
    ? buildLocationKey(activeCoordinates.latitude, activeCoordinates.longitude)
    : null;

  return (
    <div className="scroll-row scroll-row--faded pb-1">
      {favorites.map((favorite) => {
        const isActive = favorite.location_key === activeKey;
        return (
          <button
            key={favorite.id}
            type="button"
            className="segmented__option"
            style={{
              background: isActive ? 'var(--accent)' : 'var(--surface-2)',
              color: isActive ? 'var(--accent-content)' : 'var(--content-secondary)',
              border: '1px solid var(--border-hairline)',
            }}
            onClick={() => onSelect(favorite)}
            aria-current={isActive ? 'true' : undefined}
          >
            {favorite.display_name}
          </button>
        );
      })}
    </div>
  );
}
