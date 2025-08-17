// API Types for Jyotiṣa Calendar

export interface Place {
  place_id: string;
  description: string;
  main_text: string;
  secondary_text: string;
}

export interface PlaceDetails {
  place_id: string;
  formatted_address: string;
  lat: number;
  lng: number;
  timezone: {
    timeZoneId: string;
    timeZoneName: string;
    rawOffset: number;
    dstOffset: number;
  };
}

export interface PlanetPosition {
  lon_decimal: number;
  lon_dms: string;
  rasi: string;
  rasi_index: number;
  nakshatra: string;
  nak_index: number;
  pada: number;
  retrograde: boolean;
  motion_state: string;
  changedNakshatra: boolean;
  changedPada: boolean;
  changedRasi: boolean;
  speed_deg_per_day?: number;
}

export interface NakshatraInfo {
  name: string;
  name_sanskrit: string;
  name_spanish: string;
  pada: number;
  deity: string;
  element: string;
  color: string;
  symbol: string;
}

export interface YogaInfo {
  name: string;
  name_sanskrit: string;
  name_spanish: string;
  polarity: 'positive' | 'negative' | 'neutral';
  type: string;
  description: string;
  color: string;
}

export interface DayData {
  date: string;
  anchor_ts_local: string;
  planets: Record<string, PlanetPosition>;
  events?: CalendarEvent[];
  nakshatras?: Record<string, NakshatraInfo>;
  yogas?: YogaInfo[];
}

export interface CalendarEvent {
  type: 'nakshatra_change' | 'pada_change' | 'rasi_change' | 'retrograde_begin' | 'retrograde_end' | 'stationary';
  planet: string;
  ts_local: string;
  ts_utc: string;
  description: string;
  details?: {
    from?: string;
    to?: string;
    value?: number;
  };
}

export interface MonthlyCalendarResponse {
  year: number;
  month: number;
  place_id: string;
  anchor: string;
  units: string;
  days: DayData[];
}

export interface MotionState {
  planet: string;
  ts_local: string;
  ts_utc: string;
  speedDegPerDay: number;
  state: string;
  relativePct: number;
  event?: 'retro_begin' | 'retro_end' | 'station_exact';
}

export interface MotionStatesResponse {
  start: string;
  end: string;
  tzname: string;
  step_minutes: number;
  planets: string[];
  mode: string;
  states: MotionState[];
}

export interface PlanetInfo {
  name: string;
  name_sanskrit: string;
  name_spanish: string;
  symbol: string;
  color: string;
  baseline: number;
}

export interface PlanetSpeed {
  planet: string;
  name_sanskrit: string;
  name_spanish: string;
  speed_deg_per_day: number;
  motion_state: string;
  is_retrograde: boolean;
  change_date?: string;
}

// Constants
export const PLANETS: Record<string, PlanetInfo> = {
  Sun: { 
    name: 'Sun', 
    name_sanskrit: 'Sūrya', 
    name_spanish: 'Sol',
    symbol: '☉', 
    color: '#f59e0b', 
    baseline: 1.0 
  },
  Moon: { 
    name: 'Moon', 
    name_sanskrit: 'Chandra', 
    name_spanish: 'Luna',
    symbol: '☽', 
    color: '#3b82f6', 
    baseline: 13.2 
  },
  Mercury: { 
    name: 'Mercury', 
    name_sanskrit: 'Budha', 
    name_spanish: 'Mercurio',
    symbol: '☿', 
    color: '#10b981', 
    baseline: 1.4 
  },
  Venus: { 
    name: 'Venus', 
    name_sanskrit: 'Śukra', 
    name_spanish: 'Venus',
    symbol: '♀', 
    color: '#f97316', 
    baseline: 1.2 
  },
  Mars: { 
    name: 'Mars', 
    name_sanskrit: 'Maṅgala', 
    name_spanish: 'Marte',
    symbol: '♂', 
    color: '#ef4444', 
    baseline: 0.5 
  },
  Jupiter: { 
    name: 'Jupiter', 
    name_sanskrit: 'Guru', 
    name_spanish: 'Júpiter',
    symbol: '♃', 
    color: '#8b5cf6', 
    baseline: 0.08 
  },
  Saturn: { 
    name: 'Saturn', 
    name_sanskrit: 'Śani', 
    name_spanish: 'Saturno',
    symbol: '♄', 
    color: '#6b7280', 
    baseline: 0.03 
  },
  Rahu: { 
    name: 'Rahu', 
    name_sanskrit: 'Rāhu', 
    name_spanish: 'Rahu',
    symbol: '☊', 
    color: '#1f2937', 
    baseline: 0.05 
  },
  Ketu: { 
    name: 'Ketu', 
    name_sanskrit: 'Ketu', 
    name_spanish: 'Ketu',
    symbol: '☋', 
    color: '#374151', 
    baseline: 0.05 
  },
};

export const NAKSHATRAS: Record<string, NakshatraInfo> = {
  'Ashwini': {
    name: 'Ashwini',
    name_sanskrit: 'Aśvinī',
    name_spanish: 'Ashwini',
    pada: 1,
    deity: 'Ashwini Kumaras',
    element: 'Fire',
    color: '#ef4444',
    symbol: '🐎'
  },
  'Bharani': {
    name: 'Bharani',
    name_sanskrit: 'Bharaṇī',
    name_spanish: 'Bharani',
    pada: 1,
    deity: 'Yama',
    element: 'Earth',
    color: '#8b5cf6',
    symbol: '🕊️'
  },
  'Krittika': {
    name: 'Krittika',
    name_sanskrit: 'Kṛttikā',
    name_spanish: 'Krittika',
    pada: 1,
    deity: 'Agni',
    element: 'Fire',
    color: '#f59e0b',
    symbol: '🔥'
  },
  'Rohini': {
    name: 'Rohini',
    name_sanskrit: 'Rohiṇī',
    name_spanish: 'Rohini',
    pada: 1,
    deity: 'Brahma',
    element: 'Earth',
    color: '#10b981',
    symbol: '🌱'
  },
  'Mrigashira': {
    name: 'Mrigashira',
    name_sanskrit: 'Mṛgaśira',
    name_spanish: 'Mrigashira',
    pada: 1,
    deity: 'Soma',
    element: 'Water',
    color: '#3b82f6',
    symbol: '🦌'
  },
  'Ardra': {
    name: 'Ardra',
    name_sanskrit: 'Ārdrā',
    name_spanish: 'Ardra',
    pada: 1,
    deity: 'Rudra',
    element: 'Water',
    color: '#6366f1',
    symbol: '💧'
  },
  'Punarvasu': {
    name: 'Punarvasu',
    name_sanskrit: 'Punarvasu',
    name_spanish: 'Punarvasu',
    pada: 1,
    deity: 'Aditi',
    element: 'Air',
    color: '#06b6d4',
    symbol: '🏹'
  },
  'Pushya': {
    name: 'Pushya',
    name_sanskrit: 'Puṣya',
    name_spanish: 'Pushya',
    pada: 1,
    deity: 'Brihaspati',
    element: 'Fire',
    color: '#f97316',
    symbol: '🌸'
  },
  'Ashlesha': {
    name: 'Ashlesha',
    name_sanskrit: 'Āśleṣā',
    name_spanish: 'Ashlesha',
    pada: 1,
    deity: 'Nagas',
    element: 'Water',
    color: '#059669',
    symbol: '🐍'
  },
  'Magha': {
    name: 'Magha',
    name_sanskrit: 'Maghā',
    name_spanish: 'Magha',
    pada: 1,
    deity: 'Pitris',
    element: 'Fire',
    color: '#dc2626',
    symbol: '👑'
  },
  'Purva Phalguni': {
    name: 'Purva Phalguni',
    name_sanskrit: 'Pūrva Phalgunī',
    name_spanish: 'Purva Phalguni',
    pada: 1,
    deity: 'Bhaga',
    element: 'Fire',
    color: '#ea580c',
    symbol: '🌺'
  },
  'Uttara Phalguni': {
    name: 'Uttara Phalguni',
    name_sanskrit: 'Uttara Phalgunī',
    name_spanish: 'Uttara Phalguni',
    pada: 1,
    deity: 'Aryaman',
    element: 'Air',
    color: '#0891b2',
    symbol: '🌿'
  },
  'Hasta': {
    name: 'Hasta',
    name_sanskrit: 'Hasta',
    name_spanish: 'Hasta',
    pada: 1,
    deity: 'Savitar',
    element: 'Air',
    color: '#7c3aed',
    symbol: '✋'
  },
  'Chitra': {
    name: 'Chitra',
    name_sanskrit: 'Citrā',
    name_spanish: 'Chitra',
    pada: 1,
    deity: 'Vishvakarma',
    element: 'Fire',
    color: '#be185d',
    symbol: '💎'
  },
  'Swati': {
    name: 'Swati',
    name_sanskrit: 'Svātī',
    name_spanish: 'Swati',
    pada: 1,
    deity: 'Vayu',
    element: 'Air',
    color: '#0d9488',
    symbol: '🌪️'
  },
  'Vishakha': {
    name: 'Vishakha',
    name_sanskrit: 'Viśākhā',
    name_spanish: 'Vishakha',
    pada: 1,
    deity: 'Indra & Agni',
    element: 'Fire',
    color: '#b91c1c',
    symbol: '🏛️'
  },
  'Anuradha': {
    name: 'Anuradha',
    name_sanskrit: 'Anurādhā',
    name_spanish: 'Anuradha',
    pada: 1,
    deity: 'Mitra',
    element: 'Earth',
    color: '#92400e',
    symbol: '⭐'
  },
  'Jyeshtha': {
    name: 'Jyeshtha',
    name_sanskrit: 'Jyeṣṭhā',
    name_spanish: 'Jyeshtha',
    pada: 1,
    deity: 'Indra',
    element: 'Water',
    color: '#1e40af',
    symbol: '⚡'
  },
  'Mula': {
    name: 'Mula',
    name_sanskrit: 'Mūla',
    name_spanish: 'Mula',
    pada: 1,
    deity: 'Nirrti',
    element: 'Water',
    color: '#7c2d12',
    symbol: '🌱'
  },
  'Purva Ashadha': {
    name: 'Purva Ashadha',
    name_sanskrit: 'Pūrva Āṣāḍhā',
    name_spanish: 'Purva Ashadha',
    pada: 1,
    deity: 'Apas',
    element: 'Water',
    color: '#0369a1',
    symbol: '🌊'
  },
  'Uttara Ashadha': {
    name: 'Uttara Ashadha',
    name_sanskrit: 'Uttara Āṣāḍhā',
    name_spanish: 'Uttara Ashadha',
    pada: 1,
    deity: 'Vishvedevas',
    element: 'Earth',
    color: '#a16207',
    symbol: '🐘'
  },
  'Shravana': {
    name: 'Shravana',
    name_sanskrit: 'Śravaṇa',
    name_spanish: 'Shravana',
    pada: 1,
    deity: 'Vishnu',
    element: 'Air',
    color: '#1d4ed8',
    symbol: '👂'
  },
  'Dhanishtha': {
    name: 'Dhanishtha',
    name_sanskrit: 'Dhaniṣṭhā',
    name_spanish: 'Dhanishtha',
    pada: 1,
    deity: 'Vasus',
    element: 'Earth',
    color: '#9a3412',
    symbol: '🥁'
  },
  'Shatabhisha': {
    name: 'Shatabhisha',
    name_sanskrit: 'Śatabhiṣā',
    name_spanish: 'Shatabhisha',
    pada: 1,
    deity: 'Varuna',
    element: 'Water',
    color: '#0c4a6e',
    symbol: '💊'
  },
  'Purva Bhadrapada': {
    name: 'Purva Bhadrapada',
    name_sanskrit: 'Pūrva Bhādrapadā',
    name_spanish: 'Purva Bhadrapada',
    pada: 1,
    deity: 'Aja Ekapada',
    element: 'Fire',
    color: '#dc2626',
    symbol: '🔥'
  },
  'Uttara Bhadrapada': {
    name: 'Uttara Bhadrapada',
    name_sanskrit: 'Uttara Bhādrapadā',
    name_spanish: 'Uttara Bhadrapada',
    pada: 1,
    deity: 'Ahir Budhnya',
    element: 'Water',
    color: '#1e293b',
    symbol: '🐍'
  },
  'Revati': {
    name: 'Revati',
    name_sanskrit: 'Revatī',
    name_spanish: 'Revati',
    pada: 1,
    deity: 'Pushan',
    element: 'Water',
    color: '#0f766e',
    symbol: '🐟'
  }
};

export const YOGAS: Record<string, YogaInfo> = {
  'Amrita Siddhi': {
    name: 'Amrita Siddhi',
    name_sanskrit: 'Amṛta Siddhi',
    name_spanish: 'Amrita Siddhi',
    polarity: 'positive',
    type: 'vara+nakshatra',
    description: 'Yoga auspicioso para todas las actividades',
    color: '#10b981'
  },
  'Guru Pushya': {
    name: 'Guru Pushya',
    name_sanskrit: 'Guru Puṣya',
    name_spanish: 'Guru Pushya',
    polarity: 'positive',
    type: 'vara+nakshatra',
    description: 'Excelente para educación y negocios',
    color: '#8b5cf6'
  },
  'Ravi Pushya': {
    name: 'Ravi Pushya',
    name_sanskrit: 'Ravi Puṣya',
    name_spanish: 'Ravi Pushya',
    polarity: 'positive',
    type: 'sun+nakshatra',
    description: 'Ideal para actividades espirituales',
    color: '#f59e0b'
  },
  'Dagdha': {
    name: 'Dagdha',
    name_sanskrit: 'Dagdha',
    name_spanish: 'Dagdha',
    polarity: 'negative',
    type: 'vara+tithi',
    description: 'Evitar matrimonio, viajes, nueva casa',
    color: '#ef4444'
  },
  'Visha': {
    name: 'Visha',
    name_sanskrit: 'Viṣa',
    name_spanish: 'Visha',
    polarity: 'negative',
    type: 'vara+tithi',
    description: 'Evitar procedimientos médicos y viajes',
    color: '#dc2626'
  }
};

export const ANCHOR_OPTIONS = [
  { value: 'sunrise', label: 'Amanecer' },
  { value: 'noon', label: 'Mediodía' },
  { value: 'sunset', label: 'Atardecer' },
  { value: 'midnight', label: 'Medianoche' },
  { value: 'custom', label: 'Personalizado' },
];

export const UNIT_OPTIONS = [
  { value: 'decimal', label: 'Decimal' },
  { value: 'dms', label: 'DMS' },
  { value: 'both', label: 'Ambos' },
];

export const MOTION_STATES = {
  sama: { name: 'Sama', color: '#10b981', description: 'Movimiento directo normal' },
  vakrī: { name: 'Vakrī', color: '#ef4444', description: 'Retrógrado' },
  kutila: { name: 'Kutila', color: '#f59e0b', description: 'Movimiento tortuoso' },
  vikala: { name: 'Vikala', color: '#8b5cf6', description: 'Movimiento defectuoso' },
  anuvakrī: { name: 'Anuvakrī', color: '#f97316', description: 'Ligeramente retrógrado' },
  mandatara: { name: 'Mandatara', color: '#6b7280', description: 'Muy lento' },
  manda: { name: 'Manda', color: '#374151', description: 'Lento' },
  sīghra: { name: 'Sīghra', color: '#3b82f6', description: 'Rápido' },
  atisīghra: { name: 'Atisīghra', color: '#06b6d4', description: 'Muy rápido' },
};

