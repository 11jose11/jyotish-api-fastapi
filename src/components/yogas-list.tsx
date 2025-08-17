'use client';

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { type YogaInfo } from '@/types/api';

interface YogasListProps {
  yogas: YogaInfo[];
  isLoading: boolean;
}

export function YogasList({ yogas, isLoading }: YogasListProps) {
  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            Yogas del Panchanga
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Cargando yogas...
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getPolarityColor = (polarity: string) => {
    switch (polarity) {
      case 'positive':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'negative':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'neutral':
        return 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200';
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'vara+nakshatra':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'vara+tithi':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'sun+nakshatra':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      default:
        return 'bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Yogas del Panchanga
        </CardTitle>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Combinaciones auspiciosas y desfavorables del calendario védico
        </p>
      </CardHeader>
      <CardContent>
        {yogas.length > 0 ? (
          <div className="space-y-4">
            {yogas.map((yoga, index) => (
              <div 
                key={index}
                className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h4 className="font-semibold text-slate-900 dark:text-slate-100 mb-1">
                      {yoga.name}
                    </h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                      {yoga.name_sanskrit} • {yoga.name_spanish}
                    </p>
                    <p className="text-sm text-slate-700 dark:text-slate-300">
                      {yoga.description}
                    </p>
                  </div>
                  <div className="flex flex-col items-end space-y-2 ml-4">
                    <Badge 
                      variant="secondary" 
                      className={`text-xs ${getPolarityColor(yoga.polarity)}`}
                    >
                      {yoga.polarity === 'positive' ? 'Auspicioso' : 
                       yoga.polarity === 'negative' ? 'Desfavorable' : 'Neutral'}
                    </Badge>
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${getTypeColor(yoga.type)}`}
                    >
                      {yoga.type}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500 dark:text-slate-400">
            No hay yogas activos en este período
          </div>
        )}
      </CardContent>
    </Card>
  );
}
