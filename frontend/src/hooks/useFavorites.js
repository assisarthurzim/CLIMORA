import { useCallback, useEffect, useState } from 'react';
import { favoritesService } from '@/services/favoritesService';
import { buildLocationKey } from '@/utils/location';

export function useFavorites() {
  const [favorites, setFavorites] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const reload = useCallback(async () => {
    setIsLoading(true);
    try {
      setFavorites(await favoritesService.list());
      setError(null);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const findByCoordinates = useCallback(
    (coordinates) => {
      if (!coordinates) return null;
      const key = buildLocationKey(coordinates.latitude, coordinates.longitude);
      return favorites.find((favorite) => favorite.location_key === key) ?? null;
    },
    [favorites],
  );

  const add = useCallback(
    async (city) => {
      const created = await favoritesService.add(city);
      setFavorites((current) => [...current, created]);
      return created;
    },
    [],
  );

  const remove = useCallback(async (favoriteId) => {
    await favoritesService.remove(favoriteId);
    setFavorites((current) => current.filter((favorite) => favorite.id !== favoriteId));
  }, []);

  const rename = useCallback(async (favoriteId, label) => {
    const updated = await favoritesService.update(favoriteId, { label });
    setFavorites((current) =>
      current.map((favorite) => (favorite.id === favoriteId ? updated : favorite)),
    );
    return updated;
  }, []);

  return { favorites, isLoading, error, reload, findByCoordinates, add, remove, rename };
}
