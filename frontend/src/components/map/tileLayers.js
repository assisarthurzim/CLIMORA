/**
 * Free, key-free tile sources. Google and Mapbox look better but require a
 * billed API key, which would be the only paid dependency in the project.
 */
export const BASE_LAYERS = [
  {
    id: 'streets',
    label: 'Ruas',
    light: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
    dark: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}{r}.png',
    attribution: '&copy; OpenStreetMap, &copy; CARTO',
    maxZoom: 20,
    darkFilter: true,
  },
  {
    id: 'detailed',
    label: 'Detalhado',
    light: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    dark: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19,
    darkFilter: true,
  },
  {
    id: 'satellite',
    label: 'Satélite',
    light:
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    dark: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri',
    maxZoom: 19,
    darkFilter: false,
    // Satellite imagery carries no place names, so labels ride on top.
    overlay:
      'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
  },
];

export const DEFAULT_LAYER_ID = 'streets';
