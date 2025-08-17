'use client';

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { type PlanetSpeed, PLANETS } from '@/types/api';

interface PlanetSpeedsTableProps {
  speeds: PlanetSpeed[];
  isLoading: boolean;
}

export function PlanetSpeedsTable({ speeds, isLoading }: PlanetSpeedsTableProps) {
  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            Velocidades Planetarias
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Cargando velocidades...
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getSpeedColor = (speed: number, planetName: string) => {
    const planet = PLANETS[planetName];
    if (!planet) return 'text-slate-600';
    
    const baseline = planet.baseline;
    const ratio = speed / baseline;
    
    if (ratio > 1.5) return 'text-green-600 dark:text-green-400';
    if (ratio > 1.2) return 'text-blue-600 dark:text-blue-400';
    if (ratio < 0.5) return 'text-red-600 dark:text-red-400';
    if (ratio < 0.8) return 'text-orange-600 dark:text-orange-400';
    return 'text-slate-600 dark:text-slate-400';
  };

  const getMotionStateColor = (state: string) => {
    switch (state.toLowerCase()) {
      case 'sama':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'vakrī':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'kutila':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'vikala':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'anuvakrī':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      case 'mandatara':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
      case 'manda':
        return 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200';
      case 'sīghra':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'atisīghra':
        return 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200';
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Velocidades Planetarias
        </CardTitle>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Velocidades actuales de los navagrahas (9 planetas)
        </p>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700">
                <th className="text-left py-3 px-2 font-medium text-slate-700 dark:text-slate-300">
                  Planeta
                </th>
                <th className="text-left py-3 px-2 font-medium text-slate-700 dark:text-slate-300">
                  Sánscrito
                </th>
                <th className="text-left py-3 px-2 font-medium text-slate-700 dark:text-slate-300">
                  Español
                </th>
                <th className="text-right py-3 px-2 font-medium text-slate-700 dark:text-slate-300">
                  Velocidad (°/día)
                </th>
                <th className="text-center py-3 px-2 font-medium text-slate-700 dark:text-slate-300">
                  Estado
                </th>
                <th className="text-center py-3 px-2 font-medium text-slate-700 dark:text-slate-300">
                  Retrógrado
                </th>
              </tr>
            </thead>
            <tbody>
              {speeds.map((speed) => {
                const planetInfo = PLANETS[speed.planet];
                return (
                  <tr 
                    key={speed.planet} 
                    className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50"
                  >
                    <td className="py-3 px-2">
                      <div className="flex items-center space-x-2">
                        <span 
                          className="text-lg"
                          style={{ color: planetInfo?.color }}
                        >
                          {planetInfo?.symbol}
                        </span>
                        <span className="font-medium text-slate-900 dark:text-slate-100">
                          {speed.planet}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-2 text-slate-700 dark:text-slate-300">
                      {speed.name_sanskrit}
                    </td>
                    <td className="py-3 px-2 text-slate-700 dark:text-slate-300">
                      {speed.name_spanish}
                    </td>
                    <td className="py-3 px-2 text-right">
                      <span className={`font-mono ${getSpeedColor(speed.speed_deg_per_day, speed.planet)}`}>
                        {speed.speed_deg_per_day.toFixed(4)}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-center">
                      <Badge 
                        variant="secondary" 
                        className={`text-xs ${getMotionStateColor(speed.motion_state)}`}
                      >
                        {speed.motion_state}
                      </Badge>
                    </td>
                    <td className="py-3 px-2 text-center">
                      {speed.is_retrograde ? (
                        <Badge variant="destructive" className="text-xs">
                          Sí
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          No
                        </Badge>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {speeds.length === 0 && (
          <div className="text-center py-8 text-slate-500 dark:text-slate-400">
            No hay datos de velocidades disponibles
          </div>
        )}
      </CardContent>
    </Card>
  );
}
