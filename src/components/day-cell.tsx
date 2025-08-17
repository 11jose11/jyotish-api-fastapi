'use client';

import React from 'react';
import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { PLANETS, NAKSHATRAS, YOGAS, type PlanetPosition, type DayData } from '@/types/api';

interface DayCellProps {
  date: Date;
  dayData?: DayData;
  selectedPlanets: string[];
  units: string;
  onDayClick: (date: Date, dayData?: DayData) => void;
  isCurrentMonth: boolean;
}

export function DayCell({
  date,
  dayData,
  selectedPlanets,
  units,
  onDayClick,
  isCurrentMonth
}: DayCellProps) {
  const formatPosition = (planet: PlanetPosition) => {
    switch (units) {
      case 'decimal':
        return `${planet.lon_decimal.toFixed(2)}°`;
      case 'dms':
        return planet.lon_dms;
      case 'both':
        return `${planet.lon_decimal.toFixed(2)}° (${planet.lon_dms})`;
      default:
        return `${planet.lon_decimal.toFixed(2)}°`;
    }
  };

  const getChangeBadges = (planet: PlanetPosition) => {
    const badges = [];
    if (planet.changedNakshatra) {
      badges.push(
        <Badge key="nakshatra" variant="secondary" className="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
          N
        </Badge>
      );
    }
    if (planet.changedPada) {
      badges.push(
        <Badge key="pada" variant="secondary" className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
          P
        </Badge>
      );
    }
    if (planet.changedRasi) {
      badges.push(
        <Badge key="rasi" variant="secondary" className="text-xs bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
          R
        </Badge>
      );
    }
    return badges;
  };

  const getNakshatraInfo = (planet: PlanetPosition) => {
    const nakshatraInfo = NAKSHATRAS[planet.nakshatra];
    if (!nakshatraInfo) return null;
    
    return {
      name: nakshatraInfo.name_spanish,
      pada: planet.pada,
      symbol: nakshatraInfo.symbol,
      color: nakshatraInfo.color
    };
  };

  const getTooltipContent = () => {
    if (!dayData) return 'Sin datos';

    const changes = dayData.events?.map(event => {
      const time = format(new Date(event.ts_local), 'HH:mm');
      return `${event.planet}: ${event.description} @ ${time}`;
    }) || [];

    const yogas = dayData.yogas?.map(yoga => 
      `${yoga.name_spanish} (${yoga.polarity === 'positive' ? 'Auspicioso' : 'Desfavorable'})`
    ) || [];

    return (
      <div className="space-y-2">
        <div className="font-semibold">{format(date, 'EEEE, d MMMM yyyy', { locale: { code: 'es' } })}</div>
        
        {changes.length > 0 && (
          <div className="space-y-1">
            <div className="font-medium text-sm">Cambios:</div>
            {changes.map((change, index) => (
              <div key={index} className="text-xs">{change}</div>
            ))}
          </div>
        )}
        
        {yogas.length > 0 && (
          <div className="space-y-1">
            <div className="font-medium text-sm">Yogas:</div>
            {yogas.map((yoga, index) => (
              <div key={index} className="text-xs">{yoga}</div>
            ))}
          </div>
        )}
        
        {changes.length === 0 && yogas.length === 0 && (
          <div className="text-xs text-slate-500">Sin cambios</div>
        )}
      </div>
    );
  };

  const dayNumber = format(date, 'd');
  const isToday = format(date, 'yyyy-MM-dd') === format(new Date(), 'yyyy-MM-dd');

  // Check if there are any yogas for this day
  const hasYogas = dayData?.yogas && dayData.yogas.length > 0;
  const hasPositiveYogas = hasYogas && dayData.yogas.some(y => y.polarity === 'positive');
  const hasNegativeYogas = hasYogas && dayData.yogas.some(y => y.polarity === 'negative');

  // Get background color based on yogas
  const getBackgroundColor = () => {
    if (hasPositiveYogas && !hasNegativeYogas) {
      return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
    }
    if (hasNegativeYogas && !hasPositiveYogas) {
      return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
    }
    if (hasPositiveYogas && hasNegativeYogas) {
      return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
    }
    return '';
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            onClick={() => onDayClick(date, dayData)}
            className={`
              aspect-square border border-slate-200 dark:border-slate-600 rounded-lg p-2 text-sm cursor-pointer
              transition-colors hover:bg-slate-50 dark:hover:bg-slate-700
              ${!isCurrentMonth ? 'bg-slate-50 dark:bg-slate-800 text-slate-400' : ''}
              ${isCurrentMonth ? getBackgroundColor() : ''}
              ${isToday ? 'ring-2 ring-blue-500' : ''}
            `}
          >
            {/* Day number */}
            <div className={`font-medium mb-1 ${isToday ? 'text-blue-600 dark:text-blue-400' : ''}`}>
              {dayNumber}
            </div>

            {/* Yogas indicator */}
            {hasYogas && (
              <div className="flex gap-1 mb-1">
                {hasPositiveYogas && (
                  <Badge variant="secondary" className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                    +
                  </Badge>
                )}
                {hasNegativeYogas && (
                  <Badge variant="secondary" className="text-xs bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                    -
                  </Badge>
                )}
              </div>
            )}

            {/* Planet positions with nakshatras */}
            {dayData && selectedPlanets.length > 0 && (
              <div className="space-y-1">
                {selectedPlanets.slice(0, 3).map(planetName => {
                  const planet = dayData.planets[planetName];
                  if (!planet) return null;

                  const planetInfo = PLANETS[planetName];
                  const nakshatraInfo = getNakshatraInfo(planet);
                  
                  return (
                    <div key={planetName} className="space-y-1">
                      {/* Planet position */}
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1">
                          <span style={{ color: planetInfo.color }}>{planetInfo.symbol}</span>
                          <span className="truncate">{formatPosition(planet)}</span>
                        </div>
                        <div className="flex gap-1">
                          {getChangeBadges(planet)}
                          {planet.retrograde && (
                            <Badge variant="destructive" className="text-xs">
                              R
                            </Badge>
                          )}
                        </div>
                      </div>
                      
                      {/* Nakshatra and pada */}
                      {nakshatraInfo && (
                        <div className="flex items-center justify-between text-xs">
                          <div className="flex items-center gap-1">
                            <span>{nakshatraInfo.symbol}</span>
                            <span className="truncate" style={{ color: nakshatraInfo.color }}>
                              {nakshatraInfo.name}
                            </span>
                          </div>
                          <Badge 
                            variant="outline" 
                            className="text-xs"
                            style={{ borderColor: nakshatraInfo.color, color: nakshatraInfo.color }}
                          >
                            P{nakshatraInfo.pada}
                          </Badge>
                        </div>
                      )}
                    </div>
                  );
                })}
                
                {selectedPlanets.length > 3 && (
                  <div className="text-xs text-slate-500">
                    +{selectedPlanets.length - 3} más
                  </div>
                )}
              </div>
            )}

            {/* Loading state */}
            {!dayData && isCurrentMonth && (
              <div className="text-xs text-slate-400">
                Cargando...
              </div>
            )}
          </div>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs">
          {getTooltipContent()}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
