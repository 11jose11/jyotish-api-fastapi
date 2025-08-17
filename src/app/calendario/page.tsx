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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-6xl font-bold text-slate-900 dark:text-slate-100 mb-4">
            Calendario Jyotiṣa
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-3xl mx-auto">
            Calendario védico con posiciones planetarias precisas usando Swiss Ephemeris en modo sideral Lahiri
          </p>
        </div>

        {/* Controls Bar */}
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

        {/* Calendar Grid */}
        <div className="relative mb-8">
          <MonthGrid
            selectedDate={selectedDate}
            calendarData={calendarData?.days}
            selectedPlanets={selectedPlanets}
            units={units}
            onDayClick={handleDayClick}
            isLoading={isCalendarLoading}
          />
        </div>

        {/* Additional Data Section */}
        <div className="space-y-8 mb-8">
          {/* Planet Speeds Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                Velocidades Planetarias
              </h2>
              <button
                onClick={handleExportSpeedsCSV}
                disabled={!speedsData || isSpeedsLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                Exportar CSV
              </button>
            </div>
            
            {/* Chart and Table Grid */}
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

          {/* Yogas Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                Yogas del Panchanga
              </h2>
              <button
                onClick={handleExportYogasCSV}
                disabled={!yogasData || isYogasLoading}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                Exportar CSV
              </button>
            </div>
            <YogasList 
              yogas={yogasData?.yogas || []} 
              isLoading={isYogasLoading} 
            />
          </div>
        </div>

        {/* Legend */}
        <Legend />

        {/* Day Details Modal */}
        {selectedDay && (
          <DayDetailsModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            date={selectedDay.date}
            dayData={selectedDay.dayData}
            placeName={placeDetails?.formatted_address}
            timezone={placeDetails?.timezone?.timeZoneId}
            units={units}
            selectedPlanets={selectedPlanets}
          />
        )}

        {/* Print Styles */}
        <style jsx global>{`
          @media print {
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
      </div>
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
