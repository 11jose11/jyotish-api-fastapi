'use client';

import React from 'react';
import { ChevronLeft, ChevronRight, Calendar, Download, Printer, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PlaceAutocomplete } from '@/components/place-autocomplete';
import { PLANETS, ANCHOR_OPTIONS, UNIT_OPTIONS, type Place } from '@/types/api';
import { formatMonthYear } from '@/hooks/use-calendar';

interface ControlsBarProps {
  selectedPlace: Place | null;
  onPlaceSelect: (place: Place) => void;
  selectedDate: Date;
  onNavigateMonth: (direction: 'prev' | 'next') => void;
  onGoToToday: () => void;
  anchor: string;
  onAnchorChange: (anchor: string) => void;
  units: string;
  onUnitsChange: (units: string) => void;
  selectedPlanets: string[];
  onPlanetsChange: (planets: string[]) => void;
  customTime: string;
  onCustomTimeChange: (time: string) => void;
  onExportCSV: () => void;
  onPrint: () => void;
  isLoading: boolean;
}

export function ControlsBar({
  selectedPlace,
  onPlaceSelect,
  selectedDate,
  onNavigateMonth,
  onGoToToday,
  anchor,
  onAnchorChange,
  units,
  onUnitsChange,
  selectedPlanets,
  onPlanetsChange,
  customTime,
  onCustomTimeChange,
  onExportCSV,
  onPrint,
  isLoading
}: ControlsBarProps) {
  const handlePlanetToggle = (planet: string) => {
    if (selectedPlanets.includes(planet)) {
      onPlanetsChange(selectedPlanets.filter(p => p !== planet));
    } else {
      onPlanetsChange([...selectedPlanets, planet]);
    }
  };

  const handleSelectAllPlanets = () => {
    onPlanetsChange(Object.keys(PLANETS));
  };

  const handleDeselectAllPlanets = () => {
    onPlanetsChange([]);
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Controles del Calendario
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Row 1: Place and Date Navigation */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Place Autocomplete */}
          <div className="space-y-2">
            <Label htmlFor="place">Ciudad</Label>
            <PlaceAutocomplete
              selectedPlace={selectedPlace}
              onPlaceSelect={onPlaceSelect}
              placeholder="Buscar ciudad..."
            />
          </div>

          {/* Date Navigation */}
          <div className="space-y-2">
            <Label>Mes/Año</Label>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onNavigateMonth('prev')}
                disabled={isLoading}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="flex-1 text-center">
                <span className="text-sm font-medium">
                  {formatMonthYear(selectedDate)}
                </span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onNavigateMonth('next')}
                disabled={isLoading}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onGoToToday}
              className="w-full"
            >
              <Calendar className="h-4 w-4 mr-2" />
              Hoy
            </Button>
          </div>

          {/* Anchor Time */}
          <div className="space-y-2">
            <Label htmlFor="anchor">Hora de Referencia</Label>
            <Select value={anchor} onValueChange={onAnchorChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ANCHOR_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {anchor === 'custom' && (
              <Input
                type="time"
                value={customTime}
                onChange={(e) => onCustomTimeChange(e.target.value)}
                className="mt-2"
              />
            )}
          </div>
        </div>

        {/* Row 2: Units and Planets */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Units */}
          <div className="space-y-2">
            <Label>Unidades de Longitud</Label>
            <RadioGroup value={units} onValueChange={onUnitsChange} className="flex gap-4">
              {UNIT_OPTIONS.map((option) => (
                <div key={option.value} className="flex items-center space-x-2">
                  <RadioGroupItem value={option.value} id={option.value} />
                  <Label htmlFor={option.value}>{option.label}</Label>
                </div>
              ))}
            </RadioGroup>
          </div>

          {/* Planets Selection */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Planetas</Label>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSelectAllPlanets}
                >
                  Todos
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDeselectAllPlanets}
                >
                  Ninguno
                </Button>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {Object.entries(PLANETS).map(([planetKey, planet]) => (
                <div key={planetKey} className="flex items-center space-x-2">
                  <Checkbox
                    id={planetKey}
                    checked={selectedPlanets.includes(planetKey)}
                    onCheckedChange={() => handlePlanetToggle(planetKey)}
                  />
                  <Label htmlFor={planetKey} className="text-sm">
                    {planet.symbol} {planet.name}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Row 3: Action Buttons */}
        <div className="flex flex-wrap gap-2">
          <Button
            onClick={onExportCSV}
            disabled={isLoading || !selectedPlace}
            variant="outline"
          >
            <Download className="h-4 w-4 mr-2" />
            Exportar CSV
          </Button>
          <Button
            onClick={onPrint}
            disabled={isLoading}
            variant="outline"
          >
            <Printer className="h-4 w-4 mr-2" />
            Imprimir
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
