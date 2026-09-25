import { useMemo } from 'react';
import { useSettings } from '@/context/SettingsContext';
import { convertTemperature, convertWindSpeed, temperatureSymbol, windSymbol } from '@/utils/units';

const EMPTY = '—';

/**
 * Formatting bound to the user's preferences, so components never have to know
 * which unit is active.
 */
export function useUnits() {
  const { settings } = useSettings();

  return useMemo(() => {
    const temperatureUnit = settings.temperature_unit;
    const windUnit = settings.wind_speed_unit;

    return {
      temperatureUnit,
      windUnit,
      temperatureSuffix: temperatureSymbol(temperatureUnit),
      windSuffix: windSymbol(windUnit),

      formatTemperature(celsius, { withUnit = false } = {}) {
        const value = convertTemperature(celsius, temperatureUnit);
        if (value === null) return EMPTY;
        return withUnit
          ? `${Math.round(value)}${temperatureSymbol(temperatureUnit)}`
          : `${Math.round(value)}°`;
      },

      formatWind(kmh) {
        const value = convertWindSpeed(kmh, windUnit);
        if (value === null) return EMPTY;
        const decimals = windUnit === 'ms' ? 1 : 0;
        return `${value.toFixed(decimals)} ${windSymbol(windUnit)}`;
      },

      convertTemperature: (celsius) => convertTemperature(celsius, temperatureUnit),
      convertWind: (kmh) => convertWindSpeed(kmh, windUnit),
    };
  }, [settings.temperature_unit, settings.wind_speed_unit]);
}
