export const APP_NAME = import.meta.env.VITE_APP_NAME ?? 'Climora';
export const APP_TAGLINE = 'Inteligência climática para o seu dia.';

export const THEMES = Object.freeze({
  LIGHT: 'light',
  DARK: 'dark',
});

export const STORAGE_KEYS = Object.freeze({
  THEME: 'climora:theme',
});

export const ROUTES = Object.freeze({
  LANDING: '/',
  LOGIN: '/entrar',
  REGISTER: '/criar-conta',
  DASHBOARD: '/painel',
  FORGOT_PASSWORD: '/recuperar-senha',
  ASSISTANT: '/assistente',
  PROFILE: '/perfil',
});

// Used when the browser denies geolocation, so the dashboard always has
// something to show on first load.
export const DEFAULT_LOCATION = Object.freeze({
  latitude: -23.5505,
  longitude: -46.6333,
});
