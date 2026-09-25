import { useEffect, useState } from 'react';
import { Icon } from '@/components/ui/Icon';
import { insightsService } from '@/services/insightsService';

const SEVERITY_STYLES = {
  positive: { color: 'var(--positive)', background: 'rgba(47, 163, 107, 0.12)' },
  warning: { color: 'var(--warning)', background: 'var(--warning-quiet)' },
  info: { color: 'var(--accent)', background: 'var(--accent-quiet)' },
};

export function InsightsPanel({ coordinates }) {
  const [insights, setInsights] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!coordinates) return undefined;

    let active = true;
    setIsLoading(true);

    insightsService
      .forLocation(coordinates)
      .then((data) => active && setInsights(data))
      .catch(() => active && setInsights([]))
      .finally(() => active && setIsLoading(false));

    return () => {
      active = false;
    };
  }, [coordinates?.latitude, coordinates?.longitude]);

  if (isLoading || insights.length === 0) {
    return null;
  }

  return (
    <section className="mt-3 mt-md-4">
      <h2 className="type-label mb-3">Insights do dia</h2>
      <div className="row g-3">
        {insights.map((insight) => {
          const style = SEVERITY_STYLES[insight.severity] ?? SEVERITY_STYLES.info;
          return (
            <div className="col-12 col-md-6" key={insight.id}>
              <div className="surface climora-tile h-100 p-3 d-flex gap-3">
                <span
                  className="d-inline-flex align-items-center justify-content-center flex-shrink-0"
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: 'var(--radius-md)',
                    background: style.background,
                  }}
                >
                  <Icon name={insight.icon} size={18} style={{ color: style.color }} />
                </span>
                <div>
                  <span className="d-block fw-medium">{insight.title}</span>
                  <span className="d-block small" style={{ color: 'var(--content-secondary)' }}>
                    {insight.description}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
