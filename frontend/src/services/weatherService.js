import { httpClient } from './httpClient';

export const weatherService = {
  async searchCities(query, limit = 5) {
    const { data } = await httpClient.get('/weather/search', { params: { q: query, limit } });
    return data;
  },

  async reverseLookup({ latitude, longitude }) {
    const { data } = await httpClient.get('/weather/reverse', {
      params: { lat: latitude, lon: longitude },
    });
    return data;
  },

  async getSnapshot({ latitude, longitude }) {
    const { data } = await httpClient.get('/weather/snapshot', {
      params: { lat: latitude, lon: longitude },
    });
    return data;
  },

  async getAirQuality({ latitude, longitude }) {
    const { data } = await httpClient.get('/weather/air-quality', {
      params: { lat: latitude, lon: longitude },
    });
    return data;
  },
};
