import { Icon } from '@/components/ui/Icon';
import { WeatherIcon } from '@/components/weather/WeatherIcon';
import { useUnits } from '@/hooks/useUnits';
import { capitalize, formatTime } from '@/utils/formatters';

export function WeatherHero({ location, current, favoriteSlot }) {
  const { formatTemperature } = useUnits();

  return (
    <section className="surface p-3 p-md-5 mb-3 mb-md-4">
      <div className="d-flex flex-column flex-md-row align-items-start justify-content-between gap-4">
        <div>
          <div className="d-flex align-items-center gap-3 mb-1">
            <h1 className="h4 fw-semibold mb-0">{location.name}</h1>
            {favoriteSlot}
          </div>
          <p className="small mb-4" style={{ color: 'var(--content-secondary)' }}>
            {[location.state, location.country].filter(Boolean).join(', ')}
          </p>

          <div className="d-flex align-items-center gap-3">
            <span className="type-hero">{formatTemperature(current.temperature)}</span>
            <WeatherIcon
              name={current.icon}
              isDay={current.is_day}
              size="3rem"
              label={current.condition}
            />
          </div>

          <p className="fs-5 mt-3 mb-1">{capitalize(current.condition)}</p>
          <p className="mb-0" style={{ color: 'var(--content-secondary)' }}>
            Sensação de {formatTemperature(current.feels_like)} · Máx{' '}
            {formatTemperature(current.temperature_max)} · Mín{' '}
            {formatTemperature(current.temperature_min)}
          </p>
        </div>

        <div className="d-flex gap-4 order-first order-md-last align-self-stretch align-self-md-start justify-content-between justify-content-md-start">
          <SunMoment icon="sun" label="Nascer do Sol" time={current.sunrise} />
          <SunMoment icon="moon" label="Pôr do Sol" time={current.sunset} />
        </div>
      </div>
    </section>
  );
}

function SunMoment({ icon, label, time }) {
  return (
    <div className="text-center">
      <span className="d-block mb-2" style={{ color: 'var(--warning)' }}>
        <Icon name={icon} size={17} />
      </span>
      <span className="type-label d-block">{label}</span>
      <span className="type-numeric d-block fw-medium">{formatTime(time)}</span>
    </div>
  );
}
