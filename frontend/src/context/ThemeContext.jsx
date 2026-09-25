import { createContext, useCallback, useEffect, useMemo, useState } from 'react';
import { STORAGE_KEYS, THEMES } from '@/utils/constants';

export const ThemeContext = createContext(null);

function resolveInitialTheme() {
  const stored = localStorage.getItem(STORAGE_KEYS.THEME);
  if (stored === THEMES.LIGHT || stored === THEMES.DARK) {
    return stored;
  }
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  return prefersDark ? THEMES.DARK : THEMES.LIGHT;
}

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(resolveInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem(STORAGE_KEYS.THEME, theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((current) => (current === THEMES.LIGHT ? THEMES.DARK : THEMES.LIGHT));
  }, []);

  const value = useMemo(
    () => ({ theme, isDark: theme === THEMES.DARK, toggleTheme }),
    [theme, toggleTheme],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
