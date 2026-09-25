import { useMemo } from 'react';
import { Chart as ChartComponent } from 'react-chartjs-2';
import '@/components/charts/chartSetup';
import { extremeLabels, nightShading, nowMarker } from '@/components/charts/chartPlugins';
import { useIsMobile } from '@/hooks/useMediaQuery';
import { useTheme } from '@/hooks/useTheme';
import { useUnits } from '@/hooks/useUnits';
import { buildLineOptions, readChartTokens } from '@/utils/chartTheme';

const VISIBLE_HOURS = 24;
// Twenty-four labels on a 360px axis are unreadable; twelve are not.
const VISIBLE_HOURS_MOBILE = 12;
const RAIN_AXIS_MAX = 100;

function formatHour(isoString) {
  return new Date(isoString).toLocaleTimeString('pt-BR', { hour: '2-digit' });
}

/**
 * A flat fill reads as decoration; a gradient that fades toward the baseline
 * makes the area feel like magnitude.
 */
function buildGradient(context, color) {
  const { ctx, chartArea } = context.chart;
  if (!chartArea) return color;

  const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
  gradient.addColorStop(0, color);
  gradient.addColorStop(1, 'transparent');
  return gradient;
}

function withAlpha(color, alpha) {
  return color.startsWith('#')
    ? `${color}${Math.round(alpha * 255).toString(16).padStart(2, '0')}`
    : color;
}

/** Marks each hour as night by comparing it with that day's sun times. */
function markNightHours(points, daily) {
  const sunTimes = new Map(
    daily.map((day) => [day.date, { sunrise: day.sunrise, sunset: day.sunset }]),
  );

  return points.map((point) => {
    const time = new Date(point.time);
    const day = sunTimes.get(point.time.slice(0, 10));
    if (!day?.sunrise || !day?.sunset) return false;
    return time < new Date(day.sunrise) || time > new Date(day.sunset);
  });
}

export function HourlyChart({ hourly, daily, metric }) {
  const { theme } = useTheme();
  const units = useUnits();
  const isMobile = useIsMobile();

  const { data, options } = useMemo(() => {
    const points = hourly.slice(0, isMobile ? VISIBLE_HOURS_MOBILE : VISIBLE_HOURS);
    const tokens = readChartTokens();

    // Only temperature and wind depend on preference; the rest are absolute.
    const convert =
      metric.id === 'temperature'
        ? units.convertTemperature
        : metric.id === 'wind'
          ? units.convertWind
          : (value) => value;
    const unitLabel =
      metric.id === 'temperature'
        ? '°'
        : metric.id === 'wind'
          ? ` ${units.windSuffix}`
          : metric.unit;
    const baseOptions = buildLineOptions(tokens, {
      unit: unitLabel,
      beginAtZero: metric.beginAtZero,
    });

    const mainDataset = {
      type: metric.type,
      label: metric.label,
      data: points.map((point) => convert(point[metric.field])),
      yAxisID: 'main',
      borderColor: tokens.accent,
      backgroundColor:
        metric.type === 'bar'
          ? tokens.accent
          : (context) => buildGradient(context, withAlpha(tokens.accent, 0.35)),
      borderWidth: 2,
      borderRadius: metric.type === 'bar' ? 4 : 0,
      fill: metric.type === 'line',
      tension: 0.35,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: tokens.accent,
      pointHoverBorderColor: tokens.surface,
      pointHoverBorderWidth: 2,
      order: 0,
    };

    // Rain chance is the piece of context that changes how you read every
    // other metric, so it rides along except when it is the subject itself.
    const showsRainContext = metric.id !== 'precipitation';
    const rainDataset = {
      type: 'bar',
      label: 'Chance de chuva',
      data: points.map((point) => point.precipitation_probability),
      yAxisID: 'rain',
      backgroundColor: withAlpha(tokens.highlight, 0.3),
      borderRadius: 3,
      barPercentage: 0.6,
      categoryPercentage: 0.8,
      order: 1,
    };

    return {
      data: {
        labels: points.map((point) => formatHour(point.time)),
        datasets: showsRainContext ? [mainDataset, rainDataset] : [mainDataset],
      },
      options: {
        ...baseOptions,
        plugins: {
          ...baseOptions.plugins,
          tooltip: {
            ...baseOptions.plugins.tooltip,
            callbacks: {
              title: (items) => `${items[0].label} · ${points[items[0].dataIndex]?.condition ?? ''}`,
              label: (context) => {
                const unit = context.dataset.yAxisID === 'rain' ? '%' : unitLabel;
                return `${context.dataset.label}: ${Math.round(context.parsed.y)}${unit}`;
              },
            },
          },
          nightShading: {
            nights: markNightHours(points, daily),
            color: withAlpha(tokens.text, 0.08),
          },
          nowMarker: { index: 0, color: tokens.muted, fontFamily: tokens.fontFamily },
          extremeLabels: {
            datasetIndex: 0,
            unit: unitLabel,
            maxColor: tokens.highlight,
            minColor: tokens.accent,
            fontFamily: tokens.fontFamily,
          },
        },
        scales: {
          ...baseOptions.scales,
          main: { ...baseOptions.scales.y, position: 'left' },
          rain: {
            display: false,
            min: 0,
            max: RAIN_AXIS_MAX,
            // A shared axis would let a 100% rain bar dwarf the temperature
            // curve, so the bars get their own hidden scale.
          },
          y: undefined,
        },
      },
    };
  }, [hourly, daily, metric, theme, units, isMobile]);

  return (
    <div style={{ height: isMobile ? 220 : 300 }}>
      <ChartComponent
        type="bar"
        data={data}
        options={options}
        plugins={[nightShading, nowMarker, extremeLabels]}
      />
    </div>
  );
}
