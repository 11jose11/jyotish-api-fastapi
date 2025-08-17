'use client';

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PLANETS, NAKSHATRAS } from '@/types/api';

export function Legend() {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Leyenda del Calendario Jyotiṣa
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Colores de Fondo */}
          <div className="space-y-3">
            <h4 className="font-medium text-slate-700 dark:text-slate-300 text-sm">
              Colores de Fondo
            </h4>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-50 border border-green-200 rounded"></div>
                <span className="text-xs">Yogas auspiciosos</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-50 border border-red-200 rounded"></div>
                <span className="text-xs">Yogas desfavorables</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-50 border border-yellow-200 rounded"></div>
                <span className="text-xs">Yogas mixtos</span>
              </div>
            </div>
          </div>
          
          {/* Indicadores */}
          <div className="space-y-3">
            <h4 className="font-medium text-slate-700 dark:text-slate-300 text-sm">
              Indicadores
            </h4>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-800">N</Badge>
                <span className="text-xs">Cambio de Nakshatra</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">P</Badge>
                <span className="text-xs">Cambio de Pada</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-xs bg-purple-100 text-purple-800">R</Badge>
                <span className="text-xs">Cambio de Rasi</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="destructive" className="text-xs">R</Badge>
                <span className="text-xs">Planeta Retrógrado</span>
              </div>
            </div>
          </div>
          
          {/* Yogas */}
          <div className="space-y-3">
            <h4 className="font-medium text-slate-700 dark:text-slate-300 text-sm">
              Yogas
            </h4>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">+</Badge>
                <span className="text-xs">Yogas positivos</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="text-xs bg-red-100 text-red-800">-</Badge>
                <span className="text-xs">Yogas negativos</span>
              </div>
            </div>
          </div>
          
          {/* Nakshatras */}
          <div className="space-y-3">
            <h4 className="font-medium text-slate-700 dark:text-slate-300 text-sm">
              Nakshatras Principales
            </h4>
            <div className="space-y-2">
              {Object.entries(NAKSHATRAS).slice(0, 6).map(([name, info]) => (
                <div key={name} className="flex items-center gap-2">
                  <span>{info.symbol}</span>
                  <span className="text-xs truncate">{info.name_spanish}</span>
                </div>
              ))}
              <div className="text-xs text-slate-500">
                ... y más
              </div>
            </div>
          </div>
        </div>

        {/* Planetas */}
        <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-700">
          <h4 className="font-medium text-slate-700 dark:text-slate-300 text-sm mb-3">
            Navagrahas (9 Planetas)
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-9 gap-2">
            {Object.entries(PLANETS).map(([name, info]) => (
              <div key={name} className="flex items-center gap-2 text-xs">
                <span 
                  className="text-lg"
                  style={{ color: info.color }}
                >
                  {info.symbol}
                </span>
                <div className="flex flex-col">
                  <span className="font-medium">{info.name_spanish}</span>
                  <span className="text-slate-500">{info.name_sanskrit}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

