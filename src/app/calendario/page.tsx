'use client';

import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { ControlsBar } from '@/components/controls-bar';
import { MonthGrid } from '@/components/month-grid';
import { DayDetailsModal } from '@/components/day-details-modal';
import { PlanetSpeedsTable } from '@/components/planet-speeds-table';
import { PlanetSpeedsChart } from '@/components/planet-speeds-chart';
import { YogasList } from '@/components/yogas-list';
import { Legend } from '@/components/legend';
import { useCalendarState, useResolvePlace, useMonthlyCalendar, useYogas, usePlanetSpeeds } from '@/hooks/use-calendar';
import { type DayData } from '@/types/api';
import { exportCalendarCSV, exportYogasCSV, exportSpeedsCSV, downloadCSV } from '@/lib/api';
import { Calendar, Activity, BarChart3, Settings, Database, Globe, Clock } from 'lucide-react';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

function CalendarPage() {
  const {
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
    navigateMonth,
    goToToday
  } = useCalendarState();

  const [selectedDay, setSelectedDay] = useState<{ date: Date; dayData?: DayData } | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Resolve place details when place is selected
  const { data: resolvedPlace } = useResolvePlace(selectedPlace?.place_id || null);

  useEffect(() => {
    if (resolvedPlace) {
      setPlaceDetails(resolvedPlace);
    }
  }, [resolvedPlace, setPlaceDetails]);

  // Calendar data query
  const calendarParams = {
    year: selectedDate.getFullYear(),
    month: selectedDate.getMonth() + 1,
    place_id: selectedPlace?.place_id || null,
    anchor: anchor === 'custom' ? `custom:${customTime}` : anchor,
    units,
    planets: selectedPlanets
  };

  const { data: calendarData, isLoading: isCalendarLoading } = useMonthlyCalendar(calendarParams);

  // Yogas data query
  const monthStart = startOfMonth(selectedDate);
  const monthEnd = endOfMonth(selectedDate);
  const yogasParams = {
    start: format(monthStart, 'yyyy-MM-dd'),
    end: format(monthEnd, 'yyyy-MM-dd'),
    place_id: selectedPlace?.place_id || null,
    granularity: 'day',
    includeNotes: true
  };

  const { data: yogasData, isLoading: isYogasLoading } = useYogas(yogasParams);

  // Planet speeds data query
  const speedsParams = {
    start: format(monthStart, 'yyyy-MM-dd'),
    end: format(monthEnd, 'yyyy-MM-dd'),
    place_id: selectedPlace?.place_id || null,
    planets: selectedPlanets
  };

  const { data: speedsData, isLoading: isSpeedsLoading } = usePlanetSpeeds(speedsParams);

  // Handle day click
  const handleDayClick = (date: Date, dayData?: DayData) => {
    setSelectedDay({ date, dayData });
    setIsModalOpen(true);
  };

  // Export CSV
  const handleExportCSV = () => {
    if (!calendarData || !selectedPlace) return;

    const csvContent = exportCalendarCSV(calendarData, selectedPlanets);
    const filename = `jyotish-calendar-${selectedDate.getFullYear()}-${String(selectedDate.getMonth() + 1).padStart(2, '0')}.csv`;
    downloadCSV(csvContent, filename);
  };

  // Export Yogas CSV
  const handleExportYogasCSV = () => {
    if (!yogasData || !selectedPlace) return;

    const csvContent = exportYogasCSV(yogasData);
    const filename = `jyotish-yogas-${selectedDate.getFullYear()}-${String(selectedDate.getMonth() + 1).padStart(2, '0')}.csv`;
    downloadCSV(csvContent, filename);
  };

  // Export Speeds CSV
  const handleExportSpeedsCSV = () => {
    if (!speedsData || !selectedPlace) return;

    const csvContent = exportSpeedsCSV(speedsData);
    const filename = `jyotish-speeds-${selectedDate.getFullYear()}-${String(selectedDate.getMonth() + 1).padStart(2, '0')}.csv`;
    downloadCSV(csvContent, filename);
  };

  // Print calendar
  const handlePrint = () => {
    window.print();
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft') {
        navigateMonth('prev');
      } else if (event.key === 'ArrowRight') {
        navigateMonth('next');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [navigateMonth]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Modern App Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50 backdrop-blur-lg bg-white/95 dark:bg-slate-800/95">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2.5 rounded-xl shadow-lg">
                  <Calendar className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
                    Jyotiṣa Analytics
                  </h1>
                  <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
                    Vedic Astronomy Data Platform
                  </p>
                </div>
              </div>
            </div>
            
            {/* Status Indicators */}
            <div className="hidden md:flex items-center space-x-3">
              <div className="flex items-center space-x-2 px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                <span className="text-xs font-medium text-emerald-700 dark:text-emerald-400">Swiss Ephemeris</span>
              </div>
              <div className="flex items-center space-x-2 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <Database className="h-3 w-3 text-blue-600 dark:text-blue-400" />
                <span className="text-xs font-medium text-blue-700 dark:text-blue-400">Sidereal Lahiri</span>
              </div>
              {placeDetails && (
                <div className="flex items-center space-x-2 px-3 py-1.5 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                  <Globe className="h-3 w-3 text-purple-600 dark:text-purple-400" />
                  <span className="text-xs font-medium text-purple-700 dark:text-purple-400">{placeDetails.place?.name}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        {/* Controls Section */}
        <div className="mb-8">
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center space-x-3">
                <Settings className="h-5 w-5 text-slate-600 dark:text-slate-400" />
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Configuration Panel</h2>
              </div>
            </div>
            <div className="p-6">
              <ControlsBar
                selectedPlace={selectedPlace}
                onPlaceSelect={setSelectedPlace}
                selectedDate={selectedDate}
                onNavigateMonth={navigateMonth}
                onGoToToday={goToToday}
                anchor={anchor}
                onAnchorChange={setAnchor}
                units={units}
                onUnitsChange={setUnits}
                selectedPlanets={selectedPlanets}
                onPlanetsChange={setSelectedPlanets}
                customTime={customTime}
                onCustomTimeChange={setCustomTime}
                onExportCSV={handleExportCSV}
                onPrint={handlePrint}
                isLoading={isCalendarLoading}
              />
            </div>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mb-8">
          {/* Calendar - Takes 2/3 of the width */}
          <div className="xl:col-span-2">
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Calendar className="h-5 w-5 text-slate-600 dark:text-slate-400" />
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                      Planetary Calendar
                    </h2>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {format(selectedDate, 'MMMM yyyy')}
                  </Badge>
                </div>
              </div>
              <div className="p-6">
                <MonthGrid
                  selectedDate={selectedDate}
                  calendarData={calendarData?.days}
                  selectedPlanets={selectedPlanets}
                  units={units}
                  onDayClick={handleDayClick}
                  isLoading={isCalendarLoading}
                />
              </div>
            </div>
          </div>

          {/* Quick Stats Sidebar */}
          <div className="space-y-6">
            {/* Yogas Card */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
                <div className="flex items-center space-x-3">
                  <Activity className="h-5 w-5 text-slate-600 dark:text-slate-400" />
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Active Yogas</h3>
                </div>
              </div>
              <div className="p-6">
                <YogasList 
                  yogas={yogasData?.yogas?.slice(0, 5) || []} 
                  isLoading={isYogasLoading}
                  compact={true}
                />
                {yogasData?.yogas && yogasData.yogas.length > 5 && (
                  <button
                    onClick={handleExportYogasCSV}
                    className="mt-4 w-full text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
                  >
                    View all {yogasData.yogas.length} yogas →
                  </button>
                )}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
              <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
                <div className="flex items-center space-x-3">
                  <BarChart3 className="h-5 w-5 text-slate-600 dark:text-slate-400" />
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Statistics</h3>
                </div>
              </div>
              <div className="p-6 space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600 dark:text-slate-400">Selected Planets</span>
                  <Badge variant="secondary">{selectedPlanets.length}/9</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600 dark:text-slate-400">Active Yogas</span>
                  <Badge variant="secondary">{yogasData?.yogas?.length || 0}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600 dark:text-slate-400">Data Points</span>
                  <Badge variant="secondary">{calendarData?.days?.length || 0}</Badge>
                </div>
                {placeDetails?.timezone && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-600 dark:text-slate-400">Timezone</span>
                    <Badge variant="secondary" className="text-xs">
                      {placeDetails.timezone.timeZoneId}
                    </Badge>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Analytics Section */}
        <div className="space-y-8">
          {/* Planet Speeds Analysis */}
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <BarChart3 className="h-5 w-5 text-slate-600 dark:text-slate-400" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Planetary Motion Analysis
                  </h2>
                </div>
                <button
                  onClick={handleExportSpeedsCSV}
                  disabled={!speedsData || isSpeedsLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
                >
                  Export Data
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PlanetSpeedsChart 
                  speeds={speedsData?.planets || []} 
                  isLoading={isSpeedsLoading} 
                />
                <PlanetSpeedsTable 
                  speeds={speedsData?.planets || []} 
                  isLoading={isSpeedsLoading} 
                />
              </div>
            </div>
          </div>

          {/* Full Yogas List */}
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
            <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Activity className="h-5 w-5 text-slate-600 dark:text-slate-400" />
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                    Panchanga Yogas Analysis
                  </h2>
                </div>
                <button
                  onClick={handleExportYogasCSV}
                  disabled={!yogasData || isYogasLoading}
                  className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
                >
                  Export Data
                </button>
              </div>
            </div>
            <div className="p-6">
              <YogasList 
                yogas={yogasData?.yogas || []} 
                isLoading={isYogasLoading} 
              />
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-8">
          <Legend />
        </div>

        {/* Day Details Modal */}
        {selectedDay && (
          <DayDetailsModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            date={selectedDay.date}
            dayData={selectedDay.dayData}
            placeName={placeDetails?.place?.name}
            timezone={placeDetails?.timezone?.timeZoneId}
            units={units}
            selectedPlanets={selectedPlanets}
          />
        )}

        {/* Print Styles */}
        <style jsx global>{`
          @media print {
            header,
            .controls-bar,
            .modal,
            .planet-speeds,
            .yogas-list,
            .legend {
              display: none !important;
            }
            .calendar-grid {
              display: block !important;
            }
          }
        `}</style>
      </main>
    </div>
  );
}

export default function CalendarPageWrapper() {
  return (
    <QueryClientProvider client={queryClient}>
      <CalendarPage />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}