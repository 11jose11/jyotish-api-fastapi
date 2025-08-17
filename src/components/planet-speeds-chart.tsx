'use client';

import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { type PlanetSpeed, PLANETS } from '@/types/api';

interface PlanetSpeedsChartProps {
  speeds: PlanetSpeed[];
  isLoading: boolean;
}

export function PlanetSpeedsChart({ speeds, isLoading }: PlanetSpeedsChartProps) {
  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            Gráfico de Velocidades Planetarias
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Cargando gráfico...
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Prepare data for the chart
  const chartData = speeds.map(speed => ({
    planet: speed.planet,
    name: speed.name_spanish,
    speed: speed.speed_deg_per_day,
    isRetrograde: speed.is_retrograde,
    motionState: speed.motion_state,
    color: PLANETS[speed.planet]?.color || '#6b7280'
  }));

  // Sort by speed for better visualization
  chartData.sort((a, b) => Math.abs(b.speed) - Math.abs(a.speed));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-slate-800 p-3 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg">
          <p className="font-semibold text-slate-900 dark:text-slate-100">
            {data.name} ({data.planet})
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Velocidad: <span className="font-mono">{data.speed.toFixed(4)}°</span>/día
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Estado: {data.motionState}
          </p>
          {data.isRetrograde && (
            <p className="text-sm text-red-600 dark:text-red-400 font-medium">
              ⚠️ Retrógrado
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  const getSpeedColor = (speed: number, planetName: string) => {
    const planet = PLANETS[planetName];
    if (!planet) return '#6b7280';
    
    const baseline = planet.baseline;
    const ratio = Math.abs(speed) / baseline;
    
    if (ratio > 1.5) return '#10b981'; // green
    if (ratio > 1.2) return '#3b82f6'; // blue
    if (ratio < 0.5) return '#ef4444'; // red
    if (ratio < 0.8) return '#f97316'; // orange
    return '#6b7280'; // gray
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Gráfico de Velocidades Planetarias
        </CardTitle>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Velocidades actuales de los navagrahas (grados por día)
        </p>
      </CardHeader>
      <CardContent>
        {chartData.length > 0 ? (
          <div className="w-full h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={chartData}
                margin={{
                  top: 20,
                  right: 30,
                  left: 20,
                  bottom: 20,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="name" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  label={{ 
                    value: 'Velocidad (°/día)', 
                    angle: -90, 
                    position: 'insideLeft',
                    style: { textAnchor: 'middle' }
                  }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <ReferenceLine y={0} stroke="#e2e8f0" strokeDasharray="3 3" />
                
                {/* Lines for each planet */}
                {chartData.map((entry, index) => (
                  <Line
                    key={entry.planet}
                    type="monotone"
                    dataKey="speed"
                    data={[entry]}
                    stroke={getSpeedColor(entry.speed, entry.planet)}
                    strokeWidth={3}
                    dot={{ 
                      fill: getSpeedColor(entry.speed, entry.planet),
                      strokeWidth: 2,
                      r: 6
                    }}
                    name={`${entry.name} (${entry.speed.toFixed(2)}°)`}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500 dark:text-slate-400">
            No hay datos de velocidades disponibles para graficar
          </div>
        )}
        
        {/* Legend */}
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded"></div>
            <span>Muy rápido</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span>Rápido</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-500 rounded"></div>
            <span>Normal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span>Retrógrado/Lento</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
