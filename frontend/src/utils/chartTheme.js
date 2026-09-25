/**
 * Charts read the same design tokens as the rest of the interface, so a theme
 * change moves them along with everything else instead of leaving hardcoded
 * colours behind.
 */
function readToken(name, fallback = '') {
  if (typeof window === 'undefined') return fallback;
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}

export function readChartTokens() {
  return {
    accent: readToken('--accent', '#60a5fa'),
    accentSoft: readToken('--accent-quiet', 'rgba(96,165,250,0.14)'),
    highlight: readToken('--warning', '#fbbf24'),
    grid: readToken('--border-subtle', 'rgba(255,255,255,0.09)'),
    text: readToken('--content-secondary', '#a9b4c4'),
    muted: readToken('--content-muted', '#6d7a8d'),
    surface: readToken('--surface-2', '#172033'),
    fontFamily: readToken('--font-display', 'sans-serif'),
  };
}

export function buildLineOptions(tokens, { unit = '', beginAtZero = false } = {}) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: tokens.surface,
        titleColor: tokens.text,
        bodyColor: tokens.text,
        borderColor: tokens.grid,
        borderWidth: 1,
        padding: 10,
        displayColors: false,
        callbacks: {
          label: (context) => `${Math.round(context.parsed.y)}${unit}`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: {
          color: tokens.muted,
          font: { family: tokens.fontFamily, size: 11 },
          maxRotation: 0,
          autoSkipPadding: 16,
        },
        border: { color: tokens.grid },
      },
      y: {
        beginAtZero,
        grid: { color: tokens.grid, drawTicks: false },
        ticks: {
          color: tokens.muted,
          font: { family: tokens.fontFamily, size: 11 },
          padding: 8,
          callback: (value) => `${Math.round(value)}${unit}`,
        },
        border: { display: false },
      },
    },
  };
}
