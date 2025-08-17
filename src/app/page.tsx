import React from 'react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-6xl font-bold text-slate-900 dark:text-slate-100 mb-4">
            Jyotiṣa Calendar
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Calendario védico con posiciones planetarias precisas usando Swiss Ephemeris en modo sideral Lahiri
          </p>
        </div>
        
        <div className="text-center">
          <a 
            href="/calendario"
            className="inline-block bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Abrir Calendario
          </a>
        </div>
      </div>
    </div>
  );
}
