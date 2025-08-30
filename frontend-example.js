// 🌐 Jyotish API Frontend Integration Example
// Para usar con tu frontend en Vercel: https://jyotish-content-manager.vercel.app

const API_BASE = 'https://jyotish-api-ndcfqrjivq-uc.a.run.app';

// ============================================================================
// 🚀 FUNCIÓN PRINCIPAL PARA HACER REQUESTS A LA API
// ============================================================================

async function fetchFromJyotishAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  const defaultOptions = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'x-client-info': 'jyotish-frontend-v1.0.0',
      // Agregar API key si es necesario
      // 'apikey': 'your-api-key-here'
    },
    credentials: 'include', // Para cookies si las usas
  };

  const finalOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  };

  try {
    const response = await fetch(url, finalOptions);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// ============================================================================
// 🧘‍♂️ FUNCIONES PARA PANCHANGA Y YOGAS
// ============================================================================

/**
 * Detectar yogas para una fecha y ubicación específica
 * @param {string} date - Fecha en formato YYYY-MM-DD
 * @param {number} latitude - Latitud en grados decimales
 * @param {number} longitude - Longitud en grados decimales
 * @param {number} altitude - Altitud en metros (opcional)
 */
async function detectYogas(date, latitude, longitude, altitude = 0) {
  const params = new URLSearchParams({
    date,
    latitude: latitude.toString(),
    longitude: longitude.toString(),
    altitude: altitude.toString()
  });
  
  return await fetchFromJyotishAPI(`/v1/panchanga/yogas/detect?${params}`);
}

/**
 * Obtener panchanga preciso para una fecha
 * @param {string} date - Fecha en formato YYYY-MM-DD
 * @param {number} latitude - Latitud en grados decimales
 * @param {number} longitude - Longitud en grados decimales
 * @param {string} referenceTime - Tiempo de referencia: sunrise, sunset, noon, midnight
 */
async function getPrecisePanchanga(date, latitude, longitude, referenceTime = 'sunrise') {
  const params = new URLSearchParams({
    date,
    latitude: latitude.toString(),
    longitude: longitude.toString(),
    reference_time: referenceTime
  });
  
  return await fetchFromJyotishAPI(`/v1/panchanga/precise/daily?${params}`);
}

/**
 * Detectar yogas usando POST (para datos complejos)
 * @param {Object} data - Datos de la petición
 */
async function detectYogasPost(data) {
  return await fetchFromJyotishAPI('/v1/panchanga/yogas/detect', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

// ============================================================================
// 💪 FUNCIONES PARA CHESTA BALA
// ============================================================================

/**
 * Calcular Chesta Bala para una fecha
 * @param {string} date - Fecha en formato YYYY-MM-DD
 * @param {number} latitude - Latitud en grados decimales
 * @param {number} longitude - Longitud en grados decimales
 */
async function calculateChestaBala(date, latitude, longitude) {
  const params = new URLSearchParams({
    date,
    latitude: latitude.toString(),
    longitude: longitude.toString()
  });
  
  return await fetchFromJyotishAPI(`/v1/chesta-bala/calculate?${params}`);
}

/**
 * Obtener resumen de Chesta Bala
 * @param {string} date - Fecha en formato YYYY-MM-DD
 * @param {number} latitude - Latitud en grados decimales
 * @param {number} longitude - Longitud en grados decimales
 */
async function getChestaBalaSummary(date, latitude, longitude) {
  const params = new URLSearchParams({
    date,
    latitude: latitude.toString(),
    longitude: longitude.toString()
  });
  
  return await fetchFromJyotishAPI(`/v1/chesta-bala/summary?${params}`);
}

// ============================================================================
// 📅 FUNCIONES PARA CALENDARIO
// ============================================================================

/**
 * Obtener calendario diario
 * @param {string} date - Fecha en formato YYYY-MM-DD
 * @param {number} latitude - Latitud en grados decimales
 * @param {number} longitude - Longitud en grados decimales
 */
async function getDailyCalendar(date, latitude, longitude) {
  const params = new URLSearchParams({
    date,
    latitude: latitude.toString(),
    longitude: longitude.toString()
  });
  
  return await fetchFromJyotishAPI(`/v1/calendar/day?${params}`);
}

/**
 * Obtener calendario mensual
 * @param {number} year - Año
 * @param {number} month - Mes (1-12)
 * @param {number} latitude - Latitud en grados decimales
 * @param {number} longitude - Longitud en grados decimales
 */
async function getMonthlyCalendar(year, month, latitude, longitude) {
  const params = new URLSearchParams({
    year: year.toString(),
    month: month.toString(),
    latitude: latitude.toString(),
    longitude: longitude.toString()
  });
  
  return await fetchFromJyotishAPI(`/v1/calendar/month?${params}`);
}

// ============================================================================
// 🌟 FUNCIONES PARA EFEMÉRIDES
// ============================================================================

/**
 * Obtener posiciones planetarias
 * @param {string} date - Fecha en formato YYYY-MM-DD
 * @param {string} time - Hora en formato HH:MM:SS
 * @param {number} latitude - Latitud en grados decimales
 * @param {number} longitude - Longitud en grados decimales
 * @param {Array} planets - Lista de planetas (opcional)
 */
async function getPlanetaryPositions(date, time, latitude, longitude, planets = []) {
  const params = new URLSearchParams({
    date,
    time,
    latitude: latitude.toString(),
    longitude: longitude.toString()
  });
  
  if (planets.length > 0) {
    planets.forEach(planet => params.append('planets[]', planet));
  }
  
  return await fetchFromJyotishAPI(`/v1/ephemeris/planets?${params}`);
}

// ============================================================================
// 🔄 FUNCIONES PARA MOVIMIENTO PLANETARIO
// ============================================================================

/**
 * Obtener velocidades planetarias
 * @param {string} date - Fecha en formato YYYY-MM-DD
 * @param {number} latitude - Latitud en grados decimales
 * @param {number} longitude - Longitud en grados decimales
 */
async function getPlanetarySpeeds(date, latitude, longitude) {
  const params = new URLSearchParams({
    date,
    latitude: latitude.toString(),
    longitude: longitude.toString()
  });
  
  return await fetchFromJyotishAPI(`/v1/motion/speeds?${params}`);
}

/**
 * Obtener estados de movimiento planetario
 * @param {string} date - Fecha en formato YYYY-MM-DD
 * @param {number} latitude - Latitud en grados decimales
 * @param {number} longitude - Longitud en grados decimales
 */
async function getPlanetaryStates(date, latitude, longitude) {
  const params = new URLSearchParams({
    date,
    latitude: latitude.toString(),
    longitude: longitude.toString()
  });
  
  return await fetchFromJyotishAPI(`/v1/motion/states?${params}`);
}

// ============================================================================
// 🏥 FUNCIONES DE SALUD Y MONITOREO
// ============================================================================

/**
 * Verificar estado de salud de la API
 */
async function checkAPIHealth() {
  return await fetchFromJyotishAPI('/health');
}

/**
 * Probar configuración CORS
 */
async function testCORS() {
  return await fetchFromJyotishAPI('/cors-test');
}

// ============================================================================
// 📝 EJEMPLOS DE USO
// ============================================================================

// Ejemplo 1: Detectar yogas para Marsella
async function exampleDetectYogas() {
  try {
    const yogas = await detectYogas('2025-01-15', 43.2965, 5.3698);
    console.log('Yogas detectados:', yogas);
    return yogas;
  } catch (error) {
    console.error('Error detectando yogas:', error);
  }
}

// Ejemplo 2: Obtener panchanga preciso
async function exampleGetPanchanga() {
  try {
    const panchanga = await getPrecisePanchanga('2025-01-15', 43.2965, 5.3698);
    console.log('Panchanga:', panchanga);
    return panchanga;
  } catch (error) {
    console.error('Error obteniendo panchanga:', error);
  }
}

// Ejemplo 3: Calcular Chesta Bala
async function exampleChestaBala() {
  try {
    const chestaBala = await calculateChestaBala('2025-01-15', 43.2965, 5.3698);
    console.log('Chesta Bala:', chestaBala);
    return chestaBala;
  } catch (error) {
    console.error('Error calculando Chesta Bala:', error);
  }
}

// Ejemplo 4: Calendario mensual
async function exampleMonthlyCalendar() {
  try {
    const calendar = await getMonthlyCalendar(2025, 1, 43.2965, 5.3698);
    console.log('Calendario mensual:', calendar);
    return calendar;
  } catch (error) {
    console.error('Error obteniendo calendario:', error);
  }
}

// ============================================================================
// 🎯 FUNCIÓN DE INICIALIZACIÓN
// ============================================================================

/**
 * Inicializar y verificar la conexión con la API
 */
async function initializeAPI() {
  try {
    console.log('🔍 Verificando conexión con Jyotish API...');
    
    // Verificar salud de la API
    const health = await checkAPIHealth();
    console.log('✅ API Health:', health);
    
    // Probar CORS
    const corsTest = await testCORS();
    console.log('✅ CORS Test:', corsTest);
    
    console.log('🚀 Jyotish API inicializada correctamente');
    return true;
  } catch (error) {
    console.error('❌ Error inicializando API:', error);
    return false;
  }
}

// ============================================================================
// 📤 EXPORTAR FUNCIONES (para módulos ES6)
// ============================================================================

export {
  // Funciones principales
  fetchFromJyotishAPI,
  
  // Panchanga y Yogas
  detectYogas,
  getPrecisePanchanga,
  detectYogasPost,
  
  // Chesta Bala
  calculateChestaBala,
  getChestaBalaSummary,
  
  // Calendario
  getDailyCalendar,
  getMonthlyCalendar,
  
  // Efemérides
  getPlanetaryPositions,
  
  // Movimiento planetario
  getPlanetarySpeeds,
  getPlanetaryStates,
  
  // Salud y monitoreo
  checkAPIHealth,
  testCORS,
  
  // Ejemplos
  exampleDetectYogas,
  exampleGetPanchanga,
  exampleChestaBala,
  exampleMonthlyCalendar,
  
  // Inicialización
  initializeAPI
};

// ============================================================================
// 🌐 USO EN EL NAVEGADOR (script tag)
// ============================================================================

// Si usas este archivo como script tag, las funciones estarán disponibles globalmente
if (typeof window !== 'undefined') {
  window.JyotishAPI = {
    fetchFromJyotishAPI,
    detectYogas,
    getPrecisePanchanga,
    detectYogasPost,
    calculateChestaBala,
    getChestaBalaSummary,
    getDailyCalendar,
    getMonthlyCalendar,
    getPlanetaryPositions,
    getPlanetarySpeeds,
    getPlanetaryStates,
    checkAPIHealth,
    testCORS,
    exampleDetectYogas,
    exampleGetPanchanga,
    exampleChestaBala,
    exampleMonthlyCalendar,
    initializeAPI
  };
  
  console.log('🌐 JyotishAPI cargado globalmente');
}
