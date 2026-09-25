import { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import '@/components/charts/chartSetup';
import { useIsMobile } from '@/hooks/useMediaQuery';
import { useTheme } from '@/hooks/useTheme';
import { useUnits } from '@/hooks/useUnits';
import { buildLineOptions, readChartTokens } from '@/utils/chartTheme';
import { formatWeekday } from '@/utils/formatters';

export function WeeklyChart({ daily }) {
  const { theme } = useTheme();
  const { convertTemperature } = useUnits();
  const isMobile = useIsMobile();

  const { data, options } = useMemo(() => {
    const tokens = readChartTokens();
    const baseOptions = buildLineOptions(tokens, { unit: '°' });

    return {
      data: {
        labels: daily.map((day) => formatWeekday(day.date)),
        datasets: [
          {
            label: 'Máxima',
            data: daily.map((day) => convertTemperature(day.temperature_max)),
            borderColor: tokens.highlight,
            backgroundColor: 'transparent',
            borderWidth: 2,
            tension: 0.35,
            pointRadius: 3,
            pointBackgroundColor: tokens.highlight,
          },
          {
            label: 'Mínima',
            data: daily.map((day) => convertTemperature(day.temperature_min)),
            borderColor: tokens.accent,
            backgroundColor: tokens.accentSoft,
            borderWidth: 2,
            tension: 0.35,
            pointRadius: 3,
            pointBackgroundColor: tokens.accent,
            // Filling to the previous dataset shades the daily range.
            fill: '-1',
          },
        ],
      },
      options: {
        ...baseOptions,
        plugins: {
          ...baseOptions.plugins,
          tooltip: {
            ...baseOptions.plugins.tooltip,
            displayColors: true,
            callbacks: {
              label: (context) => `${context.dataset.label}: ${Math.round(context.parsed.y)}°`,
            },
          },
        },
      },
    };
  }, [daily, theme, convertTemperature]);

  return (
    <div style={{ height: isMobile ? 210 : 260 }}>
      <Line data={data} options={options} />
    </div>
  );
}
