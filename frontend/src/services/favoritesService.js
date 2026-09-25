import { httpClient } from './httpClient';

export const favoritesService = {
  async list(search) {
    const { data } = await httpClient.get('/favorites', {
      params: search ? { q: search } : undefined,
    });
    return data;
  },

  async add(city) {
    const { data } = await httpClient.post('/favorites', {
      name: city.name,
      latitude: city.latitude,
      longitude: city.longitude,
      state: city.state ?? null,
      country: city.country ?? null,
      country_code: city.country_code ?? null,
      timezone: city.timezone ?? null,
    });
    return data;
  },

  async update(favoriteId, changes) {
    const { data } = await httpClient.patch(`/favorites/${favoriteId}`, changes);
    return data;
  },

  async remove(favoriteId) {
    await httpClient.delete(`/favorites/${favoriteId}`);
  },
};
