import { useCallback, useEffect, useState } from 'react';

const GEOLOCATION_TIMEOUT = 8000;

/**
 * Asks the browser once for the user's position. Denial is an expected
 * outcome, not an error: the caller falls back to a default city.
 */
export function useGeolocation() {
  const [position, setPosition] = useState(null);
  const [isResolved, setIsResolved] = useState(false);

  const resolve = useCallback(() => {
    if (!navigator.geolocation) {
      setIsResolved(true);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        setPosition({ latitude: coords.latitude, longitude: coords.longitude });
        setIsResolved(true);
      },
      () => setIsResolved(true),
      { timeout: GEOLOCATION_TIMEOUT, maximumAge: 600000 },
    );
  }, []);

  useEffect(resolve, [resolve]);

  return { position, isResolved };
}
