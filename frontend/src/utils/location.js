const COORDINATE_PRECISION = 4;

/**
 * Mirrors the backend rule: a place is identified by its rounded coordinates,
 * so the client can tell whether a city is already favourited without asking.
 */
export function buildLocationKey(latitude, longitude) {
  return `${Number(latitude).toFixed(COORDINATE_PRECISION)},${Number(longitude).toFixed(
    COORDINATE_PRECISION,
  )}`;
}

export function toCoordinates(place) {
  return { latitude: place.latitude, longitude: place.longitude };
}
