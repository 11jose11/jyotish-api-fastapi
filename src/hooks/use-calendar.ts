'use client';

import { useState, useCallback, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { format, addMonths, subMonths, startOfMonth, endOfMonth, eachDayOfInterval } from 'date-fns';
import { es } from 'date-fns/locale';
import { 
  searchPlaces, 
  resolvePlace, 
  getMonthlyCalendar, 
  getMotionStates, 
  getYogas,
  getPlanetSpeeds,
  type Place, 
  type PlaceDetails, 
  type MonthlyCalendarResponse, 
  type MotionStatesResponse,
  type YogasResponse,
  type PlanetSpeedsResponse
} from '@/lib/api';
import { PLANETS, ANCHOR_OPTIONS, UNIT_OPTIONS } from '@/types/api';

// Local storage keys
const STORAGE_KEYS = {
  SELECTED_PLACE: 'jyotish-selected-place',
  SELECTED_DATE: 'jyotish-selected-date',
  ANCHOR: 'jyotish-anchor',
  UNITS: 'jyotish-units',
  SELECTED_PLANETS: 'jyotish-selected-planets',
  CUSTOM_TIME: 'jyotish-custom-time',
  MOTION_STEP: 'jyotish-motion-step',
  MOTION_PLANETS: 'jyotish-motion-planets',
};

const DEFAULT_PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu'];

// Calendar state hook
export function useCalendarState() {
  const [selectedDate, setSelectedDate] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEYS.SELECTED_DATE);
      return stored ? new Date(stored) : new Date();
    }
    return new Date();
  });

  const [selectedPlace, setSelectedPlace] = useState<Place | null>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEYS.SELECTED_PLACE);
      return stored ? JSON.parse(stored) : null;
    }
    return null;
  });

  const [placeDetails, setPlaceDetails] = useState<PlaceDetails | null>(null);

  const [anchor, setAnchor] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.ANCHOR) || 'sunrise';
    }
    return 'sunrise';
  });

  const [units, setUnits] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.UNITS) || 'both';
    }
    return 'both';
  });

  const [selectedPlanets, setSelectedPlanets] = useState<string[]>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEYS.SELECTED_PLANETS);
      return stored ? JSON.parse(stored) : DEFAULT_PLANETS;
    }
    return DEFAULT_PLANETS;
  });

  const [customTime, setCustomTime] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.CUSTOM_TIME) || '06:00';
    }
    return '06:00';
  });

  const [motionStep, setMotionStep] = useState(() => {
    if (typeof window !== 'undefined') {
      return parseInt(localStorage.getItem(STORAGE_KEYS.MOTION_STEP) || '60');
    }
    return 60;
  });

  const [motionPlanets, setMotionPlanets] = useState<string[]>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEYS.MOTION_PLANETS);
      return stored ? JSON.parse(stored) : DEFAULT_PLANETS;
    }
    return DEFAULT_PLANETS;
  });

  // Persist state to localStorage
  useEffect(() => {
    if (selectedPlace) {
      localStorage.setItem(STORAGE_KEYS.SELECTED_PLACE, JSON.stringify(selectedPlace));
    }
  }, [selectedPlace]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.SELECTED_DATE, selectedDate.toISOString());
  }, [selectedDate]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.ANCHOR, anchor);
  }, [anchor]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.UNITS, units);
  }, [units]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.SELECTED_PLANETS, JSON.stringify(selectedPlanets));
  }, [selectedPlanets]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.CUSTOM_TIME, customTime);
  }, [customTime]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.MOTION_STEP, motionStep.toString());
  }, [motionStep]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.MOTION_PLANETS, JSON.stringify(motionPlanets));
  }, [motionPlanets]);

  const navigateMonth = useCallback((direction: 'prev' | 'next') => {
    setSelectedDate(prev => direction === 'prev' ? subMonths(prev, 1) : addMonths(prev, 1));
  }, []);

  const goToToday = useCallback(() => {
    setSelectedDate(new Date());
  }, []);

  return {
    selectedDate,
    setSelectedDate,
    selectedPlace,
    setSelectedPlace,
    placeDetails,
    setPlaceDetails,
    anchor,
    setAnchor,
    units,
    setUnits,
    selectedPlanets,
    setSelectedPlanets,
    customTime,
    setCustomTime,
    motionStep,
    setMotionStep,
    motionPlanets,
    setMotionPlanets,
    navigateMonth,
    goToToday,
  };
}

// Place autocomplete hook
export function usePlaceAutocomplete(query: string) {
  return useQuery({
    queryKey: ['places', 'autocomplete', query],
    queryFn: () => searchPlaces(query),
    enabled: query.length >= 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Place resolution hook
export function useResolvePlace(placeId: string | null) {
  return useQuery({
    queryKey: ['places', 'resolve', placeId],
    queryFn: () => resolvePlace(placeId!),
    enabled: !!placeId,
    staleTime: 30 * 60 * 1000, // 30 minutes
    gcTime: 60 * 60 * 1000, // 1 hour
  });
}

// Monthly calendar hook
export function useMonthlyCalendar(params: {
  year: number;
  month: number;
  place_id: string | null;
  anchor: string;
  units: string;
  planets: string[];
}) {
  const queryClient = useQueryClient();
  const { year, month, place_id, anchor, units, planets } = params;

  // Prefetch next and previous months
  useEffect(() => {
    if (place_id) {
      const nextMonth = month === 12 ? { year: year + 1, month: 1 } : { year, month: month + 1 };
      const prevMonth = month === 1 ? { year: year - 1, month: 12 } : { year, month: month - 1 };

      queryClient.prefetchQuery({
        queryKey: ['calendar', 'month', place_id, nextMonth.year, nextMonth.month, anchor, units, planets.sort().join(',')],
        queryFn: () => getMonthlyCalendar({ ...nextMonth, place_id, anchor, units, planets }),
        staleTime: 5 * 60 * 1000,
      });

      queryClient.prefetchQuery({
        queryKey: ['calendar', 'month', place_id, prevMonth.year, prevMonth.month, anchor, units, planets.sort().join(',')],
        queryFn: () => getMonthlyCalendar({ ...prevMonth, place_id, anchor, units, planets }),
        staleTime: 5 * 60 * 1000,
      });
    }
  }, [queryClient, year, month, place_id, anchor, units, planets]);

  return useQuery({
    queryKey: ['calendar', 'month', place_id, year, month, anchor, units, planets.sort().join(',')],
    queryFn: () => getMonthlyCalendar({ year, month, place_id: place_id!, anchor, units, planets }),
    enabled: !!place_id && planets.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Motion states hook
export function useMotionStates(params: {
  start: string;
  end: string;
  tzname: string | null;
  step_minutes: number;
  planets: string[];
}) {
  const { start, end, tzname, step_minutes, planets } = params;

  return useQuery({
    queryKey: ['motion', 'states', start, end, tzname, step_minutes, planets.sort().join(',')],
    queryFn: () => getMotionStates({ start, end, tzname: tzname!, step_minutes, planets }),
    enabled: !!tzname && planets.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Yogas hook
export function useYogas(params: {
  start: string;
  end: string;
  place_id: string | null;
  granularity?: string;
  includeNotes?: boolean;
}) {
  const { start, end, place_id, granularity, includeNotes } = params;

  return useQuery({
    queryKey: ['yogas', start, end, place_id, granularity, includeNotes],
    queryFn: () => getYogas({ start, end, place_id: place_id!, granularity, includeNotes }),
    enabled: !!place_id,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Planet speeds hook
export function usePlanetSpeeds(params: {
  start: string;
  end: string;
  place_id: string | null;
  planets: string[];
}) {
  const { start, end, place_id, planets } = params;

  return useQuery({
    queryKey: ['planet-speeds', start, end, place_id, planets.sort().join(',')],
    queryFn: () => getPlanetSpeeds({ start, end, place_id: place_id!, planets }),
    enabled: !!place_id && planets.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Utility functions
export function getMonthDays(year: number, month: number) {
  const start = startOfMonth(new Date(year, month - 1));
  const end = endOfMonth(new Date(year, month - 1));
  return eachDayOfInterval({ start, end });
}

export function formatMonthYear(date: Date) {
  return format(date, 'MMMM yyyy', { locale: es });
}

export function formatDate(date: Date) {
  return format(date, 'yyyy-MM-dd');
}

export function getWeekdayNames() {
  return ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
}
