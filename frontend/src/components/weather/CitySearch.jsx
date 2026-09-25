import { useEffect, useRef, useState } from 'react';
import { useDebounce } from '@/hooks/useDebounce';
import { Icon } from '@/components/ui/Icon';
import { weatherService } from '@/services/weatherService';

const MIN_QUERY_LENGTH = 2;

export function CitySearch({ onSelect }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  const debouncedQuery = useDebounce(query);

  useEffect(() => {
    if (debouncedQuery.trim().length < MIN_QUERY_LENGTH) {
      setResults([]);
      return undefined;
    }

    let active = true;
    setIsSearching(true);

    weatherService
      .searchCities(debouncedQuery)
      .then((cities) => active && setResults(cities))
      .catch(() => active && setResults([]))
      .finally(() => active && setIsSearching(false));

    return () => {
      active = false;
    };
  }, [debouncedQuery]);

  // Clicking anywhere else should dismiss the suggestions.
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  function handleSelect(city) {
    onSelect(city);
    setQuery('');
    setResults([]);
    setIsOpen(false);
  }

  return (
    <div className="position-relative w-100" ref={containerRef} style={{ maxWidth: 460 }}>
      <div className="position-relative">
        <span
          className="position-absolute d-flex"
          style={{ left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--content-muted)' }}
        >
          <Icon name="search" size={16} />
        </span>
        <input
          type="search"
          className="form-control ps-5"
          placeholder="Buscar cidade"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          aria-label="Buscar cidade"
          autoComplete="off"
        />
        {isSearching ? (
          <span
            className="spinner-border spinner-border-sm position-absolute"
            style={{ right: 16, top: '50%', transform: 'translateY(-50%)', color: 'var(--accent)' }}
            aria-hidden="true"
          />
        ) : null}
      </div>

      {isOpen && results.length > 0 ? (
        <ul
          className="climora-menu list-unstyled mb-0"
          style={{ position: 'absolute', left: 0, right: 0, maxHeight: 320, overflowY: 'auto' }}
        >
          {results.map((city) => (
            <li key={`${city.location_key}-${city.name}`}>
              <button
                type="button"
                className="climora-menu__item flex-column align-items-start gap-0"
                onClick={() => handleSelect(city)}
              >
                <span style={{ fontWeight: 'var(--weight-medium)' }}>{city.name}</span>
                <span style={{ fontSize: 'var(--text-sm)', color: 'var(--content-muted)' }}>
                  {[city.state, city.country].filter(Boolean).join(', ')}
                </span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
