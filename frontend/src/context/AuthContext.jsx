import { createContext, useCallback, useEffect, useMemo, useState } from 'react';
import { authService } from '@/services/authService';
import { onSessionExpired } from '@/services/httpClient';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // The session lives in an httpOnly cookie the client cannot read, so the
  // only way to know whether one exists is to ask the API.
  useEffect(() => {
    let active = true;

    authService
      .getCurrentUser()
      .then((currentUser) => active && setUser(currentUser))
      .catch(() => active && setUser(null))
      .finally(() => active && setIsLoading(false));

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    onSessionExpired(() => setUser(null));
  }, []);

  const login = useCallback(async (credentials) => {
    const authenticated = await authService.login(credentials);
    setUser(authenticated);
    return authenticated;
  }, []);

  const register = useCallback(async (payload) => {
    const created = await authService.register(payload);
    setUser(created);
    return created;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({ user, isAuthenticated: user !== null, isLoading, login, register, logout }),
    [user, isLoading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
