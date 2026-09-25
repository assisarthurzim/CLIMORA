export const HOURLY_METRICS = [
  {
    id: 'temperature',
    label: 'Temperatura',
    field: 'temperature',
    unit: '°',
    type: 'line',
    beginAtZero: false,
  },
  {
    id: 'precipitation',
    label: 'Chuva',
    field: 'precipitation_probability',
    unit: '%',
    type: 'bar',
    beginAtZero: true,
  },
  {
    id: 'wind',
    label: 'Vento',
    field: 'wind_speed',
    unit: ' km/h',
    type: 'line',
    beginAtZero: true,
  },
  {
    id: 'humidity',
    label: 'Umidade',
    field: 'humidity',
    unit: '%',
    type: 'line',
    beginAtZero: true,
  },
  {
    id: 'pressure',
    label: 'Pressão',
    field: 'pressure',
    unit: ' hPa',
    type: 'line',
    beginAtZero: false,
  },
];

export const DEFAULT_METRIC_ID = 'temperature';
