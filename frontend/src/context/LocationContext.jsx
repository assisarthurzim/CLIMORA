import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { useGeolocation } from '@/hooks/useGeolocation';
import { DEFAULT_LOCATION } from '@/utils/constants';
import { toCoordinates } from '@/utils/location';

export const LocationContext = createContext(null);

/**
 * The active place is shared state: the dashboard sets it, and the assistant
 * needs it to know which forecast the question is about.
 */
export function LocationProvider({ children }) {
  const { position, isResolved } = useGeolocation();
  const [selectedCity, setSelectedCity] = useState(null);
  const [resolvedLocation, setResolvedLocation] = useState(null);

  const coordinates = selectedCity ?? (isResolved ? position ?? DEFAULT_LOCATION : null);

  const selectPlace = useCallback((place) => {
    setSelectedCity(toCoordinates(place));
  }, []);

  const value = useMemo(
    () => ({ coordinates, resolvedLocation, setResolvedLocation, selectPlace }),
    [coordinates, resolvedLocation, selectPlace],
  );

  return <LocationContext.Provider value={value}>{children}</LocationContext.Provider>;
}

export function useActiveLocation() {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error('useActiveLocation deve ser usado dentro de LocationProvider.');
  }
  return context;
}
