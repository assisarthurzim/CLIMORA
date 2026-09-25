import { useCallback, useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { StateMessage } from '@/components/ui/StateMessage';
import { CitySearch } from '@/components/weather/CitySearch';
import { DashboardSkeleton } from '@/components/weather/DashboardSkeleton';
import { FavoriteButton } from '@/components/weather/FavoriteButton';
import { FavoritesBar } from '@/components/weather/FavoritesBar';
import { ChartSection } from '@/components/charts/ChartSection';
import { WeatherMap } from '@/components/map/WeatherMap';
import { ForecastStrip } from '@/components/weather/ForecastStrip';
import { HistoryPanel } from '@/components/weather/HistoryPanel';
import { MetricGrid } from '@/components/weather/MetricGrid';
import { WeatherHero } from '@/components/weather/WeatherHero';
import { InsightsPanel } from '@/components/weather/InsightsPanel';
import { useActiveLocation } from '@/context/LocationContext';
import { useToast } from '@/context/ToastContext';
import { useFavorites } from '@/hooks/useFavorites';
import { useWeather } from '@/hooks/useWeather';
import { historyService } from '@/services/historyService';


export function DashboardPage() {
  const { coordinates, selectPlace, setResolvedLocation } = useActiveLocation();
  const [historyToken, setHistoryToken] = useState(0);

  const favorites = useFavorites();
  const { notify } = useToast();
  const { snapshot, isLoading, error, refresh } = useWeather(coordinates);

  // Publishing the resolved place lets the assistant name the city it is
  // answering about.
  useEffect(() => {
    if (snapshot?.location) setResolvedLocation(snapshot.location);
  }, [snapshot, setResolvedLocation]);

  // The favourite is stored with the coordinates geocoding resolved, which
  // differ slightly from the ones requested. Comparing against the resolved
  // location is what makes the star and the active chip agree.
  const resolvedLocation = snapshot?.location ?? coordinates;
  const currentFavorite = favorites.findByCoordinates(resolvedLocation);

  // History records deliberate choices only. Recording every load would fill
  // the list with the same city on each refresh.
  const openCity = useCallback(async (place, source) => {
    selectPlace(place);
    try {
      await historyService.record({
        query: place.name ?? place.city_name,
        city: {
          name: place.name ?? place.city_name,
          latitude: place.latitude,
          longitude: place.longitude,
          state: place.state,
          country: place.country,
          country_code: place.country_code,
        },
        source,
      });
      setHistoryToken((token) => token + 1);
    } catch {
      // A failed history write must not block the forecast the user asked for.
    }
  }, [selectPlace]);

  async function handleAddFavorite() {
    if (!snapshot) return;
    try {
      await favorites.add({ ...snapshot.location });
      notify({ message: `${snapshot.location.name} salva nos favoritos.`, tone: 'success' });
    } catch (error) {
      notify({ message: error.message, tone: 'error' });
    }
  }

  async function handleRemoveFavorite(favoriteId) {
    try {
      await favorites.remove(favoriteId);
      notify({ message: 'Cidade removida dos favoritos.', tone: 'info' });
    } catch (error) {
      notify({ message: error.message, tone: 'error' });
    }
  }

  return (
    <div className="container py-3 py-md-4">
      <div className="d-flex align-items-center gap-2 mb-3">
        <div className="flex-grow-1">
          <CitySearch onSelect={(city) => openCity(city, 'manual')} />
        </div>
        <Button
          variant="secondary"
          pill
          icon="refresh"
          onClick={refresh}
          disabled={isLoading || !coordinates}
          aria-label="Atualizar"
        >
          <span className="d-none d-sm-inline">Atualizar</span>
        </Button>
      </div>

      <div className="mb-3 mb-md-4">
        <FavoritesBar
          favorites={favorites.favorites}
          activeCoordinates={resolvedLocation}
          onSelect={(favorite) => openCity({ ...favorite, name: favorite.name }, 'favorite')}
        />
      </div>

      {error ? (
        <StateMessage
          icon="warning"
          title="Não foi possível carregar o clima"
          description={error}
          action={
            <Button variant="secondary" pill onClick={refresh}>
              Tentar novamente
            </Button>
          }
        />
      ) : isLoading || !snapshot ? (
        <DashboardSkeleton />
      ) : (
        <>
          <WeatherHero
            location={snapshot.location}
            current={snapshot.current}
            favoriteSlot={
              <FavoriteButton
                favorite={currentFavorite}
                onAdd={handleAddFavorite}
                onRemove={handleRemoveFavorite}
              />
            }
          />
          <MetricGrid current={snapshot.current} airQuality={snapshot.air_quality} />
          <InsightsPanel coordinates={coordinates} />
          <ForecastStrip daily={snapshot.daily} />
          <ChartSection hourly={snapshot.hourly} daily={snapshot.daily} />
          <WeatherMap location={snapshot.location} current={snapshot.current} />
        </>
      )}

      <HistoryPanel
        refreshToken={historyToken}
        onSelect={(entry) => selectPlace(entry)}
      />
    </div>
  );
}
