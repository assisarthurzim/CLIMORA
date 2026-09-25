import { useCallback, useEffect, useState } from 'react';
import { IconButton } from '@/components/ui/Button';
import { historyService } from '@/services/historyService';

const PER_PAGE = 8;

function formatMoment(isoString) {
  return new Date(isoString).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function HistoryPanel({ refreshToken, onSelect }) {
  const [entries, setEntries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const { entries: rows } = await historyService.list({ perPage: PER_PAGE });
      setEntries(rows);
    } catch {
      setEntries([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // refreshToken changes whenever a new search is recorded elsewhere.
  useEffect(() => {
    load();
  }, [load, refreshToken]);

  async function handleRemove(entryId) {
    await historyService.remove(entryId);
    setEntries((current) => current.filter((entry) => entry.id !== entryId));
  }

  async function handleClear() {
    await historyService.clear();
    setEntries([]);
  }

  return (
    <section className="surface p-3 p-md-4 mt-3 mt-md-4">
      <div className="d-flex align-items-center justify-content-between mb-3">
        <h2 className="type-label mb-0">Consultas recentes</h2>
        {entries.length > 0 ? (
          <button type="button" className="btn-climora btn-climora--ghost" onClick={handleClear}>
            Limpar
          </button>
        ) : null}
      </div>

      {isLoading ? (
        <p className="small mb-0" style={{ color: 'var(--content-muted)' }}>
          Carregando…
        </p>
      ) : entries.length === 0 ? (
        <p className="small mb-0" style={{ color: 'var(--content-muted)' }}>
          Suas buscas aparecerão aqui.
        </p>
      ) : (
        <ul className="list-unstyled mb-0 d-flex flex-column gap-1">
          {entries.map((entry) => (
            <li key={entry.id} className="d-flex align-items-center gap-2">
              <button
                type="button"
                className="btn-climora btn-climora--ghost text-start flex-grow-1 justify-content-start"
                onClick={() => onSelect(entry)}
              >
                <span className="d-block">{entry.city_name}</span>
                <span className="d-block small" style={{ color: 'var(--content-muted)' }}>
                  {[entry.state, entry.country].filter(Boolean).join(', ')} ·{' '}
                  {formatMoment(entry.created_at)}
                </span>
              </button>
              <IconButton
                name="close"
                size={14}
                label={`Remover ${entry.city_name} do histórico`}
                onClick={() => handleRemove(entry.id)}
              />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
