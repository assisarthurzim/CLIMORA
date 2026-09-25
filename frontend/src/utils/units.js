/**
 * The API always answers in Celsius and km/h. Conversion happens here, at the
 * presentation edge, so cached data stays in one canonical unit and switching
 * preference never triggers a refetch.
 */

export const TEMPERATURE_UNITS = Object.freeze({
  CELSIUS: 'celsius',
  FAHRENHEIT: 'fahrenheit',
});

export const WIND_SPEED_UNITS = Object.freeze({
  KMH: 'kmh',
  MS: 'ms',
  MPH: 'mph',
});

const TEMPERATURE_SYMBOLS = {
  [TEMPERATURE_UNITS.CELSIUS]: '°C',
  [TEMPERATURE_UNITS.FAHRENHEIT]: '°F',
};

const WIND_SYMBOLS = {
  [WIND_SPEED_UNITS.KMH]: 'km/h',
  [WIND_SPEED_UNITS.MS]: 'm/s',
  [WIND_SPEED_UNITS.MPH]: 'mph',
};

const MS_PER_KMH = 1 / 3.6;
const MPH_PER_KMH = 0.621371;

export function convertTemperature(celsius, unit) {
  if (celsius === null || celsius === undefined) return null;
  return unit === TEMPERATURE_UNITS.FAHRENHEIT ? celsius * 1.8 + 32 : celsius;
}

export function convertWindSpeed(kmh, unit) {
  if (kmh === null || kmh === undefined) return null;
  if (unit === WIND_SPEED_UNITS.MS) return kmh * MS_PER_KMH;
  if (unit === WIND_SPEED_UNITS.MPH) return kmh * MPH_PER_KMH;
  return kmh;
}

export function temperatureSymbol(unit) {
  return TEMPERATURE_SYMBOLS[unit] ?? TEMPERATURE_SYMBOLS[TEMPERATURE_UNITS.CELSIUS];
}

export function windSymbol(unit) {
  return WIND_SYMBOLS[unit] ?? WIND_SYMBOLS[WIND_SPEED_UNITS.KMH];
}
