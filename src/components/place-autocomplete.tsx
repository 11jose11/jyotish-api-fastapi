'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Search, MapPin, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { usePlaceAutocomplete } from '@/hooks/use-calendar';
import { type Place } from '@/types/api';

interface PlaceAutocompleteProps {
  selectedPlace: Place | null;
  onPlaceSelect: (place: Place) => void;
  placeholder?: string;
  className?: string;
}

export function PlaceAutocomplete({ 
  selectedPlace, 
  onPlaceSelect, 
  placeholder = "Buscar ciudad...",
  className = ""
}: PlaceAutocompleteProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const { data: places, isLoading, error } = usePlaceAutocomplete(debouncedQuery);

  const handlePlaceSelect = (place: Place) => {
    onPlaceSelect(place);
    setQuery(place.description);
    setIsOpen(false);
  };

  const handleInputChange = (value: string) => {
    setQuery(value);
    if (!isOpen) setIsOpen(true);
  };

  const handleInputFocus = () => {
    if (query.trim()) {
      setIsOpen(true);
    }
  };

  const handleClear = () => {
    setQuery('');
    onPlaceSelect(null as any);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  return (
    <div className={`relative ${className}`}>
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
            <Input
              ref={inputRef}
              type="text"
              placeholder={placeholder}
              value={query}
              onChange={(e) => handleInputChange(e.target.value)}
              onFocus={handleInputFocus}
              className="pl-10 pr-10"
            />
            {selectedPlace && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClear}
                className="absolute right-1 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
              >
                ×
              </Button>
            )}
          </div>
        </PopoverTrigger>
        
        <PopoverContent className="w-[400px] p-0" align="start">
          <div className="max-h-[300px] overflow-y-auto">
            {isLoading && (
              <div className="flex items-center justify-center p-4">
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                <span className="text-sm text-slate-600">Buscando...</span>
              </div>
            )}
            
            {error && (
              <div className="p-4 text-sm text-red-600">
                Error al buscar lugares. Inténtalo de nuevo.
              </div>
            )}
            
            {!isLoading && !error && places && places.length === 0 && debouncedQuery && (
              <div className="p-4 text-sm text-slate-600">
                No se encontraron lugares para "{debouncedQuery}"
              </div>
            )}
            
            {!isLoading && !error && places && places.length > 0 && (
              <div className="py-2">
                {places.map((place) => (
                  <button
                    key={place.place_id}
                    onClick={() => handlePlaceSelect(place)}
                    className="w-full text-left px-4 py-2 hover:bg-slate-100 dark:hover:bg-slate-800 focus:bg-slate-100 dark:focus:bg-slate-800 focus:outline-none"
                  >
                    <div className="flex items-start space-x-3">
                      <MapPin className="h-4 w-4 text-slate-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                          {place.main_text}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400 truncate">
                          {place.secondary_text}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}
