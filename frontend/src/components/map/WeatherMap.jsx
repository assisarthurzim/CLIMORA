import { useEffect, useState } from 'react';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';
import { divIcon } from 'leaflet';
import { BASE_LAYERS, DEFAULT_LAYER_ID } from '@/components/map/tileLayers';
import { useIsMobile } from '@/hooks/useMediaQuery';
import { useTheme } from '@/hooks/useTheme';
import { useUnits } from '@/hooks/useUnits';
import { capitalize } from '@/utils/formatters';

const DEFAULT_ZOOM = 12;
const FLY_DURATION = 0.8;

/**
 * Leaflet's stock marker loads its image from a relative path that bundlers
 * rewrite, which is why it so often renders broken. A DOM icon has no asset to
 * lose, and it can show the temperature directly on the map.
 */
function buildMarker(label) {
  return divIcon({
    className: '',
    html: `<span class="climora-marker">${label}</span>`,
    iconSize: [56, 32],
    iconAnchor: [28, 16],
  });
}

function RecenterOnChange({ latitude, longitude }) {
  const map = useMap();

  useEffect(() => {
    map.flyTo([latitude, longitude], DEFAULT_ZOOM, { duration: FLY_DURATION });
  }, [map, latitude, longitude]);

  return null;
}

function LayerPicker({ activeId, onChange }) {
  return (
    <div
      className="glass-surface position-absolute d-flex gap-1 p-1"
      style={{ top: 10, right: 10, zIndex: 500, borderRadius: 'var(--radius-pill)' }}
    >
      {BASE_LAYERS.map((layer) => {
        const isActive = layer.id === activeId;
        return (
          <button
            key={layer.id}
            type="button"
            className="segmented__option"
            style={{
              fontSize: 'var(--text-xs)',
              background: isActive ? 'var(--accent)' : 'transparent',
              color: isActive ? 'var(--accent-content)' : 'var(--content-secondary)',
            }}
            onClick={() => onChange(layer.id)}
            aria-pressed={isActive}
          >
            {layer.label}
          </button>
        );
      })}
    </div>
  );
}

export function WeatherMap({ location, current }) {
  const { isDark } = useTheme();
  const { formatTemperature } = useUnits();
  const isMobile = useIsMobile();
  const [layerId, setLayerId] = useState(DEFAULT_LAYER_ID);

  const layer = BASE_LAYERS.find((item) => item.id === layerId) ?? BASE_LAYERS[0];
  const center = [location.latitude, location.longitude];
  const shouldDim = isDark && layer.darkFilter;

  return (
    <section
      className="surface p-0 overflow-hidden mt-3 mt-md-4 position-relative"
      style={{ height: isMobile ? 300 : 420 }}
    >
      <LayerPicker activeId={layerId} onChange={setLayerId} />

      <MapContainer
        center={center}
        zoom={DEFAULT_ZOOM}
        scrollWheelZoom={false}
        zoomControl={false}
        style={{ height: '100%', width: '100%' }}
        className={shouldDim ? 'climora-map--dim' : undefined}
        key={location.location_key}
      >
        <TileLayer
          key={`${layer.id}-${isDark}`}
          url={isDark ? layer.dark : layer.light}
          attribution={layer.attribution}
          maxZoom={layer.maxZoom}
          // Serves @2x tiles on high-density screens, which is most of the
          // perceived sharpness.
          detectRetina
        />
        {layer.overlay ? <TileLayer url={layer.overlay} maxZoom={layer.maxZoom} /> : null}

        <Marker position={center} icon={buildMarker(formatTemperature(current.temperature))}>
          <Popup>
            <strong>{location.name}</strong>
            <br />
            {capitalize(current.condition)} · {formatTemperature(current.temperature)}
          </Popup>
        </Marker>

        <RecenterOnChange latitude={location.latitude} longitude={location.longitude} />
      </MapContainer>
    </section>
  );
}
