#!/bin/bash

# Script de despliegue para Vercel
# Jyotiṣa Calendar Frontend

set -e

echo "🚀 Desplegando Jyotiṣa Calendar Frontend en Vercel"
echo "=================================================="

# Verificar que Vercel CLI esté instalado
if ! command -v vercel &> /dev/null; then
    echo "❌ Error: Vercel CLI no está instalado"
    echo "Instala Vercel CLI con: npm i -g vercel"
    exit 1
fi

# Verificar que estemos en el directorio correcto
if [ ! -f "package.json" ] || [ ! -f "next.config.ts" ]; then
    echo "❌ Error: No estás en el directorio del proyecto Next.js"
    exit 1
fi

# Verificar que las dependencias estén instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Construir el proyecto
echo "🔨 Construyendo proyecto..."
npm run build

# Desplegar en Vercel
echo "🚀 Desplegando en Vercel..."
vercel --prod

echo ""
echo "✅ ¡Despliegue completado exitosamente!"
echo ""
echo "📋 Información del despliegue:"
echo "   - El proyecto se ha desplegado en Vercel"
echo "   - La URL se mostrará en la salida anterior"
echo ""
echo "🔧 Para configurar variables de entorno:"
echo "   vercel env add NEXT_PUBLIC_API_BASE_URL"
echo ""
echo "📊 Para ver logs:"
echo "   vercel logs"
