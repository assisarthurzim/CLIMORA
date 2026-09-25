const EMPTY = '—';

export function formatTemperature(value, { withUnit = true } = {}) {
  if (value === null || value === undefined) return EMPTY;
  return `${Math.round(value)}${withUnit ? '°' : ''}`;
}

export function formatPercent(value) {
  if (value === null || value === undefined) return EMPTY;
  return `${Math.round(value)}%`;
}

export function formatPressure(value) {
  if (value === null || value === undefined) return EMPTY;
  return `${Math.round(value)} hPa`;
}

export function formatWind(value) {
  if (value === null || value === undefined) return EMPTY;
  return `${Math.round(value)} km/h`;
}

export function formatVisibility(meters) {
  if (meters === null || meters === undefined) return EMPTY;
  if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`;
  return `${Math.round(meters)} m`;
}

export function formatPrecipitation(value) {
  if (value === null || value === undefined) return EMPTY;
  return `${value.toFixed(1)} mm`;
}

export function formatTime(isoString) {
  if (!isoString) return EMPTY;
  return new Date(isoString).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatWeekday(isoDate) {
  if (!isoDate) return EMPTY;
  const date = new Date(`${isoDate}T12:00:00`);
  return date.toLocaleDateString('pt-BR', { weekday: 'short' }).replace('.', '');
}

const UV_BANDS = [
  { max: 2, label: 'Baixo' },
  { max: 5, label: 'Moderado' },
  { max: 7, label: 'Alto' },
  { max: 10, label: 'Muito alto' },
];
const UV_EXTREME = 'Extremo';

export function describeUvIndex(value) {
  if (value === null || value === undefined) return EMPTY;
  const band = UV_BANDS.find((item) => value <= item.max);
  return `${Math.round(value)} · ${band ? band.label : UV_EXTREME}`;
}

export function capitalize(text) {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1);
}
