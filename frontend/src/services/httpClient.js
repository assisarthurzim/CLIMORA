import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
const ACCESS_CSRF_COOKIE = 'csrf_access_token';
const REFRESH_CSRF_COOKIE = 'csrf_refresh_token';
const MUTATING_METHODS = ['post', 'put', 'patch', 'delete'];
const REFRESH_PATH = '/auth/refresh';

const NETWORK_ERROR = {
  code: 'NETWORK_ERROR',
  message: 'Não foi possível conectar ao Climora. Verifique sua conexão.',
};

function readCookie(name) {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export class ApiError extends Error {
  constructor({ code, message, details, status }) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details ?? {};
    this.status = status ?? 0;
  }
}

export const httpClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// JWTs live in httpOnly cookies, so the CSRF token is the only credential the
// client can read and must echo back.
httpClient.interceptors.request.use((config) => {
  const method = (config.method ?? 'get').toLowerCase();
  if (MUTATING_METHODS.includes(method)) {
    const cookieName = config.url === REFRESH_PATH ? REFRESH_CSRF_COOKIE : ACCESS_CSRF_COOKIE;
    const csrfToken = readCookie(cookieName);
    if (csrfToken) {
      config.headers['X-CSRF-TOKEN'] = csrfToken;
    }
  }
  return config;
});

let sessionExpiredHandler = null;
let networkErrorHandler = null;

export function onSessionExpired(handler) {
  sessionExpiredHandler = handler;
}

export function onNetworkError(handler) {
  networkErrorHandler = handler;
}

// A single in-flight refresh is shared by every request that hits a 401, so a
// dashboard loading six widgets does not fire six refreshes.
let refreshRequest = null;

function refreshSession() {
  if (!refreshRequest) {
    refreshRequest = axios
      .post(`${BASE_URL}${REFRESH_PATH}`, null, {
        withCredentials: true,
        headers: { 'X-CSRF-TOKEN': readCookie(REFRESH_CSRF_COOKIE) ?? '' },
      })
      .finally(() => {
        refreshRequest = null;
      });
  }
  return refreshRequest;
}

function toApiError(error) {
  const envelope = error.response?.data?.error;

  // No response at all means the API is unreachable, not that it refused.
  if (!error.response) {
    networkErrorHandler?.();
  }

  return new ApiError({
    code: envelope?.code ?? NETWORK_ERROR.code,
    message: envelope?.message ?? NETWORK_ERROR.message,
    details: envelope?.details,
    status: error.response?.status,
  });
}

httpClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const request = error.config ?? {};
    const isExpiredSession =
      error.response?.status === 401 && error.response?.data?.error?.code === 'TOKEN_EXPIRED';
    const isRetryable = isExpiredSession && !request._retried && request.url !== REFRESH_PATH;

    if (isRetryable) {
      request._retried = true;
      try {
        await refreshSession();
        return await httpClient(request);
      } catch {
        sessionExpiredHandler?.();
        throw new ApiError({
          code: 'SESSION_EXPIRED',
          message: 'Sua sessão expirou. Entre novamente.',
          status: 401,
        });
      }
    }

    throw toApiError(error);
  },
);
