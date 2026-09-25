import { httpClient } from './httpClient';

export const systemService = {
  async getHealth() {
    const { data } = await httpClient.get('/system/health');
    return data;
  },
};
