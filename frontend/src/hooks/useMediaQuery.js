import { useEffect, useState } from 'react';

/**
 * Some responsive decisions cannot be made in CSS — a chart's pixel height, or
 * how many hours fit on screen. Those need the breakpoint in JavaScript.
 */
export function useMediaQuery(query) {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches);

  useEffect(() => {
    const list = window.matchMedia(query);
    const update = (event) => setMatches(event.matches);

    setMatches(list.matches);
    list.addEventListener('change', update);
    return () => list.removeEventListener('change', update);
  }, [query]);

  return matches;
}

export const MOBILE_QUERY = '(max-width: 767.98px)';

export function useIsMobile() {
  return useMediaQuery(MOBILE_QUERY);
}
