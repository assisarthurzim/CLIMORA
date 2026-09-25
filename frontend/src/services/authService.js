import { ApiError, httpClient } from './httpClient';

// The API speaks snake_case; the forms speak camelCase. Field errors have to
// be translated back or they would never reach the input that caused them.
const API_TO_FORM_FIELD = {
  password_confirmation: 'passwordConfirmation',
  remember_me: 'rememberMe',
};

function translateFieldErrors(error) {
  if (!(error instanceof ApiError)) {
    return error;
  }

  const details = Object.fromEntries(
    Object.entries(error.details).map(([field, message]) => [
      API_TO_FORM_FIELD[field] ?? field,
      message,
    ]),
  );

  return new ApiError({
    code: error.code,
    message: error.message,
    details,
    status: error.status,
  });
}

export const authService = {
  async register({ name, email, password, passwordConfirmation }) {
    try {
      const { data } = await httpClient.post('/auth/register', {
        name,
        email,
        password,
        password_confirmation: passwordConfirmation,
      });
      return data;
    } catch (error) {
      throw translateFieldErrors(error);
    }
  },

  async login({ email, password, rememberMe }) {
    try {
      const { data } = await httpClient.post('/auth/login', {
        email,
        password,
        remember_me: rememberMe,
      });
      return data;
    } catch (error) {
      throw translateFieldErrors(error);
    }
  },

  async logout() {
    await httpClient.post('/auth/logout');
  },

  async getCurrentUser() {
    const { data } = await httpClient.get('/auth/me');
    return data;
  },
};
