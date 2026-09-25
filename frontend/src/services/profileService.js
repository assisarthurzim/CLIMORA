import { httpClient } from './httpClient';

export const profileService = {
  async get() {
    const { data } = await httpClient.get('/profile');
    return data;
  },

  async update(changes) {
    const { data } = await httpClient.patch('/profile', changes);
    return data;
  },

  async changePassword({ currentPassword, newPassword, newPasswordConfirmation }) {
    await httpClient.put('/profile/password', {
      current_password: currentPassword,
      new_password: newPassword,
      new_password_confirmation: newPasswordConfirmation,
    });
  },

  async getSettings() {
    const { data } = await httpClient.get('/profile/settings');
    return data;
  },

  async updateSettings(changes) {
    const { data } = await httpClient.put('/profile/settings', changes);
    return data;
  },

  async deleteAccount(password) {
    await httpClient.delete('/profile', { data: { password } });
  },
};
