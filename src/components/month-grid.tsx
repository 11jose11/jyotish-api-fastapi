'use client';

import React from 'react';
import { startOfMonth, endOfMonth, eachDayOfInterval, startOfWeek, endOfWeek, isSameDay, isSameMonth } from 'date-fns';
import { DayCell } from '@/components/day-cell';
import { getWeekdayNames } from '@/hooks/use-calendar';
import { type DayData } from '@/types/api';

interface MonthGridProps {
  selectedDate: Date;
  calendarData?: DayData[];
  selectedPlanets: string[];
  units: string;
  onDayClick: (date: Date, dayData?: DayData) => void;
  isLoading: boolean;
}

export function MonthGrid({
  selectedDate,
  calendarData,
  selectedPlanets,
  units,
  onDayClick,
  isLoading
}: MonthGridProps) {
  const today = new Date();
  const monthStart = startOfMonth(selectedDate);
  const monthEnd = endOfMonth(selectedDate);
  const calendarStart = startOfWeek(monthStart);
  const calendarEnd = endOfWeek(monthEnd);
  
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });
  const weekdayNames = getWeekdayNames();

  const getDayData = (date: Date): DayData | undefined => {
    if (!calendarData) return undefined;
    const dateStr = date.toISOString().split('T')[0];
    return calendarData.find(day => day.date === dateStr);
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
      {/* Month Header */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
          {selectedDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })}
        </h2>
      </div>

      {/* Weekday Headers */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {weekdayNames.map((day) => (
          <div key={day} className="text-center py-2 font-semibold text-slate-700 dark:text-slate-300">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1">
        {days.map((date) => {
          const dayData = getDayData(date);
          const isCurrentMonth = isSameMonth(date, selectedDate);
          
          return (
            <DayCell
              key={date.toISOString()}
              date={date}
              dayData={dayData}
              selectedPlanets={selectedPlanets}
              units={units}
              onDayClick={onDayClick}
              isCurrentMonth={isCurrentMonth}
            />
          );
        })}
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white/80 dark:bg-slate-800/80 flex items-center justify-center rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="text-sm text-slate-600 dark:text-slate-400">
              Cargando calendario...
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
