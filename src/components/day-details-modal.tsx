'use client';

import React from 'react';
import { format } from 'date-fns';
import { X, Copy, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { PLANETS, type DayData, type PlanetPosition } from '@/types/api';
import { copyToClipboard, downloadCSV } from '@/lib/api';

interface DayDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  date: Date;
  dayData?: DayData;
  placeName?: string;
  timezone?: string;
  units: string;
  selectedPlanets: string[];
}

export function DayDetailsModal({
  isOpen,
  onClose,
  date,
  dayData,
  placeName,
  timezone,
  units,
  selectedPlanets
}: DayDetailsModalProps) {
  const formatPosition = (planet: PlanetPosition) => {
    switch (units) {
      case 'decimal':
        return `${planet.lon_decimal.toFixed(6)}°`;
      case 'dms':
        return planet.lon_dms;
      case 'both':
        return `${planet.lon_decimal.toFixed(6)}° (${planet.lon_dms})`;
      default:
        return `${planet.lon_decimal.toFixed(6)}°`;
    }
  };

  const getMotionStateColor = (state: string) => {
    const colors: Record<string, string> = {
      sama: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      vakrī: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      kutila: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      vikala: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      anuvakrī: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      mandatara: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
      manda: 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200',
      sīghra: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      atisīghra: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200',
    };
    return colors[state] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  };

  const copyToClipboard = async () => {
    if (!dayData) return;
    
    const text = generateTextReport();
    try {
      await navigator.clipboard.writeText(text);
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const exportDayCSV = () => {
    if (!dayData) return;
    
    const csvContent = generateCSVContent();
    const filename = `jyotish-day-${format(date, 'yyyy-MM-dd')}.csv`;
    downloadCSV(csvContent, filename);
  };

  const generateTextReport = () => {
    if (!dayData) return '';
    
    let report = `Calendario Jyotiṣa - ${format(date, 'EEEE, d MMMM yyyy', { locale: { code: 'es' } })}\n`;
    if (placeName) report += `Lugar: ${placeName}\n`;
    if (timezone) report += `Zona horaria: ${timezone}\n`;
    report += `Hora de referencia: ${dayData.anchor_ts_local}\n\n`;
    
    report += 'Posiciones Planetarias:\n';
    report += '='.repeat(50) + '\n';
    
    selectedPlanets.forEach(planetName => {
      const planet = dayData.planets[planetName];
      if (!planet) return;
      
      const planetInfo = PLANETS[planetName];
      report += `${planetInfo.symbol} ${planetName}:\n`;
      report += `  Longitud: ${formatPosition(planet)}\n`;
      report += `  Rāśi: ${planet.rasi} (${planet.rasi_index})\n`;
      report += `  Nakṣatra: ${planet.nakshatra} (${planet.nak_index})\n`;
      report += `  Pāda: ${planet.pada}\n`;
      report += `  Estado: ${planet.motion_state}\n`;
      report += `  Retrógrado: ${planet.retrograde ? 'Sí' : 'No'}\n`;
      report += '\n';
    });
    
    if (dayData.events && dayData.events.length > 0) {
      report += 'Eventos del día:\n';
      report += '='.repeat(50) + '\n';
      dayData.events.forEach(event => {
        const time = format(new Date(event.ts_local), 'HH:mm');
        report += `${time} - ${event.planet}: ${event.description}\n`;
      });
    }
    
    return report;
  };

  const generateCSVContent = () => {
    if (!dayData) return '';
    
    const headers = [
      'Planeta', 'Longitud_Decimal', 'Longitud_DMS', 'Rasi', 'Rasi_Index',
      'Nakshatra', 'Nak_Index', 'Pada', 'Retrograde', 'Motion_State',
      'Changed_Nakshatra', 'Changed_Pada', 'Changed_Rasi'
    ];
    
    const rows = selectedPlanets.map(planetName => {
      const planet = dayData.planets[planetName];
      if (!planet) return '';
      
      return [
        planetName,
        planet.lon_decimal.toFixed(6),
        planet.lon_dms,
        planet.rasi,
        planet.rasi_index,
        planet.nakshatra,
        planet.nak_index,
        planet.pada,
        planet.retrograde ? 'Sí' : 'No',
        planet.motion_state,
        planet.changedNakshatra ? 'Sí' : 'No',
        planet.changedPada ? 'Sí' : 'No',
        planet.changedRasi ? 'Sí' : 'No'
      ].join(',');
    }).filter(Boolean);
    
    return [headers.join(','), ...rows].join('\n');
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>
              Detalles del {format(date, 'EEEE, d MMMM yyyy', { locale: { code: 'es' } })}
            </span>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>

        {dayData ? (
          <div className="space-y-6">
            {/* Header Info */}
            <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                {placeName && (
                  <div>
                    <span className="font-medium">Lugar:</span> {placeName}
                  </div>
                )}
                {timezone && (
                  <div>
                    <span className="font-medium">Zona horaria:</span> {timezone}
                  </div>
                )}
                <div>
                  <span className="font-medium">Hora de referencia:</span> {dayData.anchor_ts_local}
                </div>
              </div>
            </div>

            {/* Planets Table */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Posiciones Planetarias</h3>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-slate-200 dark:border-slate-700">
                  <thead>
                    <tr className="bg-slate-50 dark:bg-slate-800">
                      <th className="border border-slate-200 dark:border-slate-700 px-3 py-2 text-left">Planeta</th>
                      <th className="border border-slate-200 dark:border-slate-700 px-3 py-2 text-left">Longitud</th>
                      <th className="border border-slate-200 dark:border-slate-700 px-3 py-2 text-left">Rāśi</th>
                      <th className="border border-slate-200 dark:border-slate-700 px-3 py-2 text-left">Nakṣatra</th>
                      <th className="border border-slate-200 dark:border-slate-700 px-3 py-2 text-left">Pāda</th>
                      <th className="border border-slate-200 dark:border-slate-700 px-3 py-2 text-left">Estado</th>
                      <th className="border border-slate-200 dark:border-slate-700 px-3 py-2 text-left">Cambios</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedPlanets.map(planetName => {
                      const planet = dayData.planets[planetName];
                      if (!planet) return null;
                      
                      const planetInfo = PLANETS[planetName];
                      return (
                        <tr key={planetName} className="hover:bg-slate-50 dark:hover:bg-slate-800">
                          <td className="border border-slate-200 dark:border-slate-700 px-3 py-2">
                            <div className="flex items-center gap-2">
                              <span style={{ color: planetInfo.color }} className="text-lg">
                                {planetInfo.symbol}
                              </span>
                              <span className="font-medium">{planetName}</span>
                              {planet.retrograde && (
                                <Badge variant="destructive" className="text-xs">
                                  R
                                </Badge>
                              )}
                            </div>
                          </td>
                          <td className="border border-slate-200 dark:border-slate-700 px-3 py-2 font-mono">
                            {formatPosition(planet)}
                          </td>
                          <td className="border border-slate-200 dark:border-slate-700 px-3 py-2">
                            {planet.rasi} ({planet.rasi_index})
                          </td>
                          <td className="border border-slate-200 dark:border-slate-700 px-3 py-2">
                            {planet.nakshatra} ({planet.nak_index})
                          </td>
                          <td className="border border-slate-200 dark:border-slate-700 px-3 py-2">
                            {planet.pada}
                          </td>
                          <td className="border border-slate-200 dark:border-slate-700 px-3 py-2">
                            <Badge className={`text-xs ${getMotionStateColor(planet.motion_state)}`}>
                              {planet.motion_state}
                            </Badge>
                          </td>
                          <td className="border border-slate-200 dark:border-slate-700 px-3 py-2">
                            <div className="flex gap-1">
                              {planet.changedNakshatra && (
                                <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                                  N
                                </Badge>
                              )}
                              {planet.changedPada && (
                                <Badge variant="secondary" className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                                  P
                                </Badge>
                              )}
                              {planet.changedRasi && (
                                <Badge variant="secondary" className="text-xs bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                                  R
                                </Badge>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Events */}
            {dayData.events && dayData.events.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Eventos del Día</h3>
                <div className="space-y-2">
                  {dayData.events.map((event, index) => {
                    const time = format(new Date(event.ts_local), 'HH:mm');
                    return (
                      <div key={index} className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-900 rounded-lg">
                        <div className="font-mono text-sm bg-white dark:bg-slate-800 px-2 py-1 rounded">
                          {time}
                        </div>
                        <div className="flex-1">
                          <span className="font-medium">{event.planet}:</span> {event.description}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4 border-t">
              <Button onClick={copyToClipboard} variant="outline">
                <Copy className="h-4 w-4 mr-2" />
                Copiar como texto
              </Button>
              <Button onClick={exportDayCSV} variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar día (CSV)
              </Button>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500">
            No hay datos disponibles para este día.
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
