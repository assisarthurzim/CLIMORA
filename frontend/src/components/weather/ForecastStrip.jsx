import { WeatherIcon } from '@/components/weather/WeatherIcon';
import { useUnits } from '@/hooks/useUnits';
import { formatPercent, formatWeekday } from '@/utils/formatters';

export function ForecastStrip({ daily }) {
  const { formatTemperature } = useUnits();

  if (daily.length === 0) return null;

  return (
    <section className="surface p-3 mt-3 mt-md-4">
      <div className="scroll-row scroll-row--faded">
        {daily.map((day, index) => (
          <div
            key={day.date}
            className="text-center px-3 py-2 flex-shrink-0"
            style={{ minWidth: 84 }}
          >
            <span className="type-label d-block">
              {index === 0 ? 'Hoje' : formatWeekday(day.date)}
            </span>
            <span className="d-block my-2">
              <WeatherIcon name={day.icon} size="1.5rem" label={day.condition} />
            </span>
            <span className="type-numeric d-block fw-medium">
              {formatTemperature(day.temperature_max)}
            </span>
            <span className="type-numeric d-block small" style={{ color: 'var(--content-muted)' }}>
              {formatTemperature(day.temperature_min)}
            </span>
            <span className="d-block small mt-1" style={{ color: 'var(--accent)' }}>
              {formatPercent(day.precipitation_probability_max)}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
