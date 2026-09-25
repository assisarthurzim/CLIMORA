/**
 * Plugins that draw the context a bare line cannot: when it is dark outside,
 * where the present moment sits, and which points are the extremes.
 */

export const nightShading = {
  id: 'nightShading',
  beforeDatasetsDraw(chart, _args, options) {
    const nights = options?.nights;
    if (!nights?.length) return;

    const { ctx, chartArea, scales } = chart;
    const xScale = scales.x;

    ctx.save();
    ctx.fillStyle = options.color ?? 'rgba(0,0,0,0.05)';

    let spanStart = null;

    nights.forEach((isNight, index) => {
      if (isNight && spanStart === null) {
        spanStart = index;
      }

      const isLast = index === nights.length - 1;
      const spanEnded = spanStart !== null && (!isNight || isLast);
      if (!spanEnded) return;

      const from = xScale.getPixelForValue(spanStart);
      const to = xScale.getPixelForValue(isNight ? index : index - 1);
      ctx.fillRect(from, chartArea.top, Math.max(to - from, 1), chartArea.bottom - chartArea.top);
      spanStart = null;
    });

    ctx.restore();
  },
};

export const nowMarker = {
  id: 'nowMarker',
  afterDatasetsDraw(chart, _args, options) {
    if (options?.index === undefined) return;

    const { ctx, chartArea, scales } = chart;
    const x = scales.x.getPixelForValue(options.index);

    ctx.save();
    ctx.strokeStyle = options.color ?? '#888888';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(x, chartArea.top);
    ctx.lineTo(x, chartArea.bottom);
    ctx.stroke();

    ctx.setLineDash([]);
    ctx.fillStyle = options.color ?? '#888888';
    ctx.font = `600 10px ${options.fontFamily ?? 'sans-serif'}`;
    ctx.textAlign = 'left';
    ctx.fillText('agora', x + 6, chartArea.top + 12);
    ctx.restore();
  },
};

export const extremeLabels = {
  id: 'extremeLabels',
  afterDatasetsDraw(chart, _args, options) {
    const datasetIndex = options?.datasetIndex ?? 0;
    const values = chart.data.datasets[datasetIndex]?.data ?? [];

    const defined = values
      .map((value, index) => ({ value, index }))
      .filter((item) => item.value !== null && item.value !== undefined);
    if (defined.length < 2) return;

    const highest = defined.reduce((a, b) => (b.value > a.value ? b : a));
    const lowest = defined.reduce((a, b) => (b.value < a.value ? b : a));

    const meta = chart.getDatasetMeta(datasetIndex);
    const { ctx } = chart;

    ctx.save();
    ctx.font = `600 11px ${options?.fontFamily ?? 'sans-serif'}`;
    ctx.textAlign = 'center';

    [
      { point: highest, color: options?.maxColor, offset: -10 },
      { point: lowest, color: options?.minColor, offset: 18 },
    ].forEach(({ point, color, offset }) => {
      const element = meta.data[point.index];
      if (!element) return;
      ctx.fillStyle = color ?? '#333333';
      ctx.fillText(`${Math.round(point.value)}${options?.unit ?? ''}`, element.x, element.y + offset);
    });

    ctx.restore();
  },
};
