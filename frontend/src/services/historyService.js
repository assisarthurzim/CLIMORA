import { httpClient } from './httpClient';

export const historyService = {
  async list({ page = 1, perPage = 20, search } = {}) {
    const response = await httpClient.get('/history', {
      params: { page, per_page: perPage, ...(search ? { q: search } : {}) },
    });
    return { entries: response.data, meta: response.meta };
  },

  async record({ query, city, source = 'manual' }) {
    const { data } = await httpClient.post('/history', {
      query,
      city_name: city.name,
      latitude: city.latitude,
      longitude: city.longitude,
      state: city.state ?? null,
      country: city.country ?? null,
      country_code: city.country_code ?? null,
      source,
    });
    return data;
  },

  async remove(entryId) {
    await httpClient.delete(`/history/${entryId}`);
  },

  async clear() {
    await httpClient.delete('/history');
  },
};
