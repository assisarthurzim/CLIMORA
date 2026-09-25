import { MetricTile } from '@/components/weather/MetricTile';
import { useUnits } from '@/hooks/useUnits';
import {
  describeUvIndex,
  formatPercent,
  formatPrecipitation,
  formatPressure,
  formatVisibility,
} from '@/utils/formatters';

export function MetricGrid({ current, airQuality }) {
  const { formatWind } = useUnits();

  const metrics = [
    {
      icon: 'humidity',
      label: 'Umidade',
      value: formatPercent(current.humidity),
    },
    {
      icon: 'pressure',
      label: 'Pressão',
      value: formatPressure(current.pressure),
    },
    {
      icon: 'wind',
      label: 'Vento',
      value: formatWind(current.wind_speed),
      hint: current.wind_direction_label ? `Direção ${current.wind_direction_label}` : null,
    },
    {
      icon: 'uv',
      label: 'Índice UV',
      value: describeUvIndex(current.uv_index),
    },
    {
      icon: 'visibility',
      label: 'Visibilidade',
      value: formatVisibility(current.visibility),
    },
    {
      icon: 'precipitation',
      label: 'Chance de chuva',
      value: formatPercent(current.precipitation_probability),
      hint: `Acumulado ${formatPrecipitation(current.precipitation)}`,
    },
    {
      icon: 'cloud-cover',
      label: 'Nebulosidade',
      value: formatPercent(current.cloud_cover),
    },
    {
      icon: 'air-quality',
      label: 'Qualidade do ar',
      value: airQuality?.category ?? '—',
      hint: airQuality?.index !== null && airQuality?.index !== undefined
        ? `Índice ${Math.round(airQuality.index)}`
        : null,
    },
  ];

  return (
    <div className="row g-2 g-md-3">
      {metrics.map((metric) => (
        <div className="col-6 col-md-4 col-xl-3" key={metric.label}>
          <MetricTile {...metric} />
        </div>
      ))}
    </div>
  );
}
