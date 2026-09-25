import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { profileService } from '@/services/profileService';
import { TEMPERATURE_UNITS, WIND_SPEED_UNITS } from '@/utils/units';

export const SettingsContext = createContext(null);

const DEFAULT_SETTINGS = Object.freeze({
  temperature_unit: TEMPERATURE_UNITS.CELSIUS,
  wind_speed_unit: WIND_SPEED_UNITS.KMH,
  language: 'pt-BR',
});

export function SettingsProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);

  useEffect(() => {
    if (!isAuthenticated) {
      setSettings(DEFAULT_SETTINGS);
      return undefined;
    }

    let active = true;
    profileService
      .getSettings()
      .then((loaded) => active && setSettings(loaded))
      .catch(() => active && setSettings(DEFAULT_SETTINGS));

    return () => {
      active = false;
    };
  }, [isAuthenticated]);

  const update = useCallback(async (changes) => {
    // Optimistic: the change is local arithmetic, so waiting on the round trip
    // would make the interface feel slower than it is.
    setSettings((current) => ({ ...current, ...changes }));
    try {
      setSettings(await profileService.updateSettings(changes));
    } catch (error) {
      setSettings(await profileService.getSettings());
      throw error;
    }
  }, []);

  const value = useMemo(() => ({ settings, update }), [settings, update]);

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings deve ser usado dentro de SettingsProvider.');
  }
  return context;
}
