import { Icon } from '@/components/ui/Icon';

// After dark, a clear sky is a moon, not a sun. Only a few conditions have a
// distinct night reading; the rest look the same either way.
const NIGHT_VARIANTS = {
  sun: 'moon',
  'sun-cloud': 'cloud-moon',
  'cloud-sun': 'cloud-moon',
  'rain-showers': 'rain-showers-night',
};

const WARM_CONDITIONS = new Set(['sun', 'sun-cloud', 'cloud-sun']);

export function WeatherIcon({ name, isDay = true, size = 28, label, strokeWidth = 1.5 }) {
  const resolved = (!isDay && NIGHT_VARIANTS[name]) || name;
  const color = isDay && WARM_CONDITIONS.has(name) ? 'var(--warning)' : 'var(--accent)';

  return <Icon name={resolved} size={size} strokeWidth={strokeWidth} style={{ color }} label={label} />;
}
