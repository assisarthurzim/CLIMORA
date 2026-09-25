import {
  AlertTriangle,
  ArrowRight,
  Check,
  ChevronDown,
  ChevronUp,
  CircleAlert,
  CloudDrizzle,
  CloudFog,
  CloudLightning,
  CloudMoon,
  CloudMoonRain,
  CloudRain,
  CloudSun,
  CloudSunRain,
  Cloudy,
  Compass,
  Droplet,
  Eye,
  Footprints,
  Gauge,
  Info,
  LayoutDashboard,
  Leaf,
  LogOut,
  MessageSquare,
  Moon,
  RefreshCw,
  Search,
  Send,
  Snowflake,
  Star,
  Sun,
  Thermometer,
  ThermometerSnowflake,
  ThermometerSun,
  Umbrella,
  UserCog,
  Wifi,
  Wind,
  X,
} from 'lucide-react';

/**
 * One icon vocabulary for the whole product. Components ask for meaning
 * ("umidade", "chuva forte") and never for a glyph, so swapping libraries or
 * refining a choice happens here instead of in twenty files.
 */
const ICONS = {
  // Weather conditions, keyed by the semantic names the API returns.
  sun: Sun,
  moon: Moon,
  'sun-cloud': CloudSun,
  'cloud-sun': CloudSun,
  'cloud-moon': CloudMoon,
  cloud: Cloudy,
  fog: CloudFog,
  drizzle: CloudDrizzle,
  sleet: CloudDrizzle,
  rain: CloudRain,
  'rain-heavy': CloudRain,
  'rain-showers': CloudSunRain,
  'rain-showers-night': CloudMoonRain,
  snow: Snowflake,
  'snow-heavy': Snowflake,
  thunderstorm: CloudLightning,
  'cloud-question': Cloudy,

  // Measurements.
  humidity: Droplet,
  pressure: Gauge,
  wind: Wind,
  uv: Sun,
  visibility: Eye,
  precipitation: CloudRain,
  'cloud-cover': Cloudy,
  'air-quality': Leaf,
  temperature: Thermometer,
  'temperature-low': ThermometerSnowflake,
  'temperature-high': ThermometerSun,
  compass: Compass,

  // Insights.
  umbrella: Umbrella,
  'person-walking': Footprints,
  droplet: Droplet,
  leaf: Leaf,
  lungs: Leaf,

  // Interface.
  dashboard: LayoutDashboard,
  assistant: MessageSquare,
  account: UserCog,
  logout: LogOut,
  search: Search,
  refresh: RefreshCw,
  send: Send,
  star: Star,
  close: X,
  check: Check,
  info: Info,
  warning: AlertTriangle,
  error: CircleAlert,
  offline: Wifi,
  'chevron-down': ChevronDown,
  'chevron-up': ChevronUp,
  'arrow-right': ArrowRight,
};

const FALLBACK = Cloudy;

export function Icon({ name, size = 16, strokeWidth = 1.75, className, style, label }) {
  const Glyph = ICONS[name] ?? FALLBACK;

  return (
    <Glyph
      size={size}
      strokeWidth={strokeWidth}
      className={className}
      style={style}
      aria-hidden={label ? undefined : true}
      aria-label={label}
      role={label ? 'img' : undefined}
    />
  );
}

export function hasIcon(name) {
  return name in ICONS;
}
