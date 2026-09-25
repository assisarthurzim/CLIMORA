import { useState } from 'react';
import { HourlyChart } from '@/components/charts/HourlyChart';
import { WeeklyChart } from '@/components/charts/WeeklyChart';
import { DEFAULT_METRIC_ID, HOURLY_METRICS } from '@/components/charts/hourlyMetrics';

const WEEKLY_TAB = { id: 'weekly', label: 'Semana' };
const TABS = [...HOURLY_METRICS, WEEKLY_TAB];

function LegendSwatch({ color, label }) {
  return (
    <span className="d-flex align-items-center gap-2">
      <span style={{ width: 14, height: 3, borderRadius: 2, background: color }} />
      {label}
    </span>
  );
}

export function ChartSection({ hourly, daily }) {
  const [activeId, setActiveId] = useState(DEFAULT_METRIC_ID);

  const hasHourly = hourly.length > 0;
  const hasDaily = daily.length > 0;

  if (!hasHourly && !hasDaily) {
    return null;
  }

  const activeMetric = HOURLY_METRICS.find((metric) => metric.id === activeId);

  return (
    <section className="surface p-3 p-md-4 mt-3 mt-md-4">
      <div className="segmented scroll-row mb-4" role="tablist">
        {TABS.map((tab) => {
          const isActive = tab.id === activeId;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={isActive}
              className="segmented__option"
              onClick={() => setActiveId(tab.id)}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {activeMetric ? (
        <HourlyChart hourly={hourly} daily={daily} metric={activeMetric} />
      ) : (
        <WeeklyChart daily={daily} />
      )}

      <p className="small mb-0 mt-3" style={{ color: 'var(--content-muted)' }}>
        {activeMetric
          ? 'Próximas 24 horas · faixas escuras indicam a noite'
          : 'Próximos 7 dias · a área mostra a amplitude entre mínima e máxima'}
      </p>
    </section>
  );
}
