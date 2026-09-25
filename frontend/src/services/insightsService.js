import { httpClient } from './httpClient';

export const insightsService = {
  async forLocation({ latitude, longitude }) {
    const { data } = await httpClient.get('/insights', {
      params: { lat: latitude, lon: longitude },
    });
    return data;
  },
};
