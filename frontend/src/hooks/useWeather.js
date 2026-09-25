import { useCallback, useEffect, useState } from 'react';
import { weatherService } from '@/services/weatherService';

/**
 * Loads a full snapshot for a coordinate pair and re-fetches when it changes.
 */
export function useWeather(coordinates) {
  const [snapshot, setSnapshot] = useState(null);
  const [isLoading, setIsLoading] = useState(Boolean(coordinates));
  const [error, setError] = useState(null);

  const load = useCallback(async (target, signal) => {
    if (!target) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await weatherService.getSnapshot(target);
      if (!signal?.aborted) setSnapshot(data);
    } catch (requestError) {
      if (!signal?.aborted) setError(requestError.message);
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    load(coordinates, controller.signal);
    return () => controller.abort();
  }, [coordinates?.latitude, coordinates?.longitude, load]);

  const refresh = useCallback(() => load(coordinates), [load, coordinates]);

  return { snapshot, isLoading, error, refresh };
}
