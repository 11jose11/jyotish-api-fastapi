# Jyotiṣa Calendar Frontend

Frontend moderno y responsive para el Calendario Jyotish, construido con Next.js 14, TypeScript, Tailwind CSS y shadcn/ui.

## 🌟 Características

- **Interfaz Moderna**: Diseño limpio y accesible con tema oscuro/claro
- **Búsqueda de Lugares**: Autocompletado con debounce de 250ms
- **Calendario Mensual**: Vista completa con posiciones planetarias
- **Detalles Interactivos**: Modal con información completa del día
- **Exportación**: CSV del mes completo y días individuales
- **Impresión**: Vista optimizada para impresión
- **Navegación por Teclado**: Flechas para cambiar mes
- **Persistencia**: Configuración guardada en localStorage
- **Responsive**: Optimizado para móvil, tablet y desktop

## 🛠️ Stack Tecnológico

- **Next.js 14** - Framework React con App Router
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Framework de estilos
- **shadcn/ui** - Componentes de UI
- **TanStack Query** - Gestión de estado y caché
- **date-fns** - Manipulación de fechas
- **Lucide React** - Iconos

## 🚀 Instalación

### Prerrequisitos

- Node.js 18+ 
- npm o yarn

### Configuración Local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd jyotish-frontend
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar variables de entorno**
```bash
# Crear .env.local
NEXT_PUBLIC_API_BASE_URL=https://jyotish-api-814110081793.us-central1.run.app
```

4. **Ejecutar en desarrollo**
```bash
npm run dev
```

La aplicación estará disponible en: http://localhost:3000

## 📁 Estructura del Proyecto

```
src/
├── app/
│   ├── calendario/
│   │   └── page.tsx          # Página principal del calendario
│   ├── globals.css           # Estilos globales
│   ├── layout.tsx            # Layout principal
│   └── page.tsx              # Página de inicio
├── components/
│   ├── ui/                   # Componentes shadcn/ui
│   ├── controls-bar.tsx      # Barra de controles
│   ├── day-cell.tsx          # Celda de día
│   ├── day-details-modal.tsx # Modal de detalles
│   ├── legend.tsx            # Leyenda
│   ├── month-grid.tsx        # Grid mensual
│   └── place-autocomplete.tsx # Autocompletado de lugares
├── hooks/
│   └── use-calendar.ts       # Hooks personalizados
└── lib/
    └── api.ts                # Configuración y tipos de API
```

## 🎯 Funcionalidades Principales

### Búsqueda de Lugares
- Autocompletado con debounce de 250ms
- Integración con Google Places API a través del backend
- Resolución automática de zona horaria

### Calendario Mensual
- Vista de 7 columnas (L-D)
- Posiciones planetarias en tiempo real
- Indicadores de cambios (Nakṣatra, Pāda, Rāśi)
- Estados de movimiento planetario
- Detección de retrogradación

### Controles Avanzados
- Selección de hora de referencia (sunrise, midnight, noon, custom)
- Unidades de longitud (decimal, DMS, both)
- Selección múltiple de planetas
- Navegación por teclado (←/→)

### Exportación e Impresión
- Exportación a CSV del mes completo
- Exportación de días individuales
- Vista de impresión optimizada
- Copia al portapapeles

## 🔧 Configuración

### Variables de Entorno

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=https://jyotish-api-814110081793.us-central1.run.app

# App Configuration (opcional)
NEXT_PUBLIC_APP_NAME=Jyotiṣa Calendar
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Personalización

#### Temas
Los temas se configuran en `src/app/globals.css` usando las variables CSS de shadcn/ui.

#### Componentes
Los componentes de UI se pueden personalizar en `src/components/ui/`.

## 📱 Responsive Design

- **Móvil**: 2 columnas en grid, controles apilados
- **Tablet**: 4-5 columnas, controles en grid
- **Desktop**: 7 columnas, controles en línea

## ♿ Accesibilidad

- Navegación por teclado (←/→ para cambiar mes)
- Anuncios ARIA para cambios de estado
- Contraste adecuado en todos los temas
- Focus visible en todos los elementos interactivos

## 🧪 Testing

```bash
# Ejecutar tests
npm test

# Tests con coverage
npm run test:coverage

# Tests en modo watch
npm run test:watch
```

## 🚀 Despliegue

### Vercel (Recomendado)

1. **Conectar repositorio**
```bash
# En Vercel Dashboard
# Importar desde GitHub
# Configurar variables de entorno
NEXT_PUBLIC_API_BASE_URL=https://jyotish-api-814110081793.us-central1.run.app
```

2. **Despliegue automático**
- Cada push a `main` despliega automáticamente
- Preview deployments para pull requests

### Otros Proveedores

#### Netlify
```bash
# build command
npm run build

# publish directory
.next
```

#### Railway
```bash
# Configurar en Railway Dashboard
# Variables de entorno automáticas
```

## 🔍 Debugging

### React Query DevTools
En desarrollo, las React Query DevTools están disponibles en la esquina inferior derecha.

### Console Logs
```bash
# Habilitar logs detallados
DEBUG=* npm run dev
```

## 📊 Performance

- **Lazy Loading**: Componentes cargados bajo demanda
- **Caching**: React Query con TTL de 5-10 minutos
- **Prefetching**: Mes siguiente precargado automáticamente
- **Optimización**: Imágenes y assets optimizados

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: Abrir issue en GitHub
- **Documentación**: Ver `/docs` en la aplicación
- **API**: Verificar endpoints en el backend

## 🔗 Enlaces Útiles

- [API Jyotiṣa](https://jyotish-api-814110081793.us-central1.run.app/docs)
- [Swiss Ephemeris](https://www.astro.com/swisseph/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)
