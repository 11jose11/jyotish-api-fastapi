# 🧹 Plan de Depuración - Archivos Obsoletos

## 📋 Análisis de Archivos

### ✅ **Archivos a MANTENER (Esenciales)**

#### **Documentación Principal:**
- ✅ `API_ENDPOINTS_COMPLETE.md` - **MANTENER** (solicitado por el usuario)
- ✅ `FRONTEND_BACKEND_CONFIG.md` - Configuración completa
- ✅ `README.md` - Documentación principal del proyecto
- ✅ `CORS_OPTIMIZATION_REPORT.md` - Reporte de optimización CORS

#### **Scripts de Despliegue:**
- ✅ `deploy-full.sh` - Despliegue completo
- ✅ `verify-deployment.sh` - Verificación de despliegue
- ✅ `setup-environment.sh` - Configuración de entorno
- ✅ `cleanup-global.sh` - Limpieza global

#### **Configuración:**
- ✅ `Dockerfile` - Configuración Docker
- ✅ `requirements.txt` - Dependencias Python
- ✅ `pyproject.toml` - Configuración del proyecto
- ✅ `env.example` - Variables de entorno de ejemplo
- ✅ `.gitignore` - Archivos ignorados por Git
- ✅ `.dockerignore` - Archivos ignorados por Docker

#### **Código de la API:**
- ✅ `app/` - Código principal de la API
- ✅ `run.py` - Script de ejecución
- ✅ `tests/` - Tests de la aplicación
- ✅ `rules/` - Reglas de negocio

#### **Frontend:**
- ✅ `src/` - Código del frontend Next.js

---

### 🗑️ **Archivos OBSOLETOS (A Eliminar)**

#### **Reportes Antiguos:**
- ❌ `AUDIT_FINAL_REPORT.md` - Reporte de auditoría antiguo
- ❌ `API_AUDIT_REPORT.md` - Reporte de auditoría de API antiguo
- ❌ `UNIFICATION_REPORT.md` - Reporte de unificación antiguo
- ❌ `SERVICES_SUMMARY.md` - Resumen de servicios antiguo
- ❌ `DEPLOYMENT_SUCCESS.md` - Reporte de éxito de despliegue antiguo

#### **Scripts de Prueba Antiguos:**
- ❌ `test-api-integration.sh` - Script de prueba de integración antiguo
- ❌ `deploy-cloud-run.sh` - Script de despliegue antiguo (reemplazado por deploy-full.sh)

#### **Archivos de Prueba Antiguos:**
- ❌ `PRUEBA_MARSEILLE_HOY.md` - Prueba específica antigua
- ❌ `PRUEBA_LIMA_1988.md` - Prueba específica antigua

#### **Middleware Obsoleto:**
- ❌ `app/middleware/cors.py` - Middleware CORS personalizado (ya no se usa)

#### **Frontend Obsoleto:**
- ❌ `frontend/` - Directorio frontend antiguo (reemplazado por src/)

---

### 🔄 **Archivos a REVISAR**

#### **Documentación:**
- 🔄 `DEPLOYMENT_GUIDE.md` - Verificar si está actualizado
- 🔄 `test-cors.sh` - Verificar si sigue siendo útil

---

## 🎯 **Plan de Acción**

### **Fase 1: Eliminación de Archivos Obsoletos**
1. Eliminar reportes antiguos
2. Eliminar scripts de prueba obsoletos
3. Eliminar archivos de prueba específicos
4. Eliminar middleware CORS obsoleto
5. Eliminar directorio frontend antiguo

### **Fase 2: Limpieza de Código**
1. Verificar referencias a archivos eliminados
2. Actualizar imports si es necesario
3. Limpiar comentarios obsoletos

### **Fase 3: Verificación**
1. Ejecutar tests para asegurar que todo funciona
2. Verificar que el despliegue sigue funcionando
3. Confirmar que la documentación está actualizada

---

## 📊 **Impacto Esperado**

### **Espacio Liberado:**
- ~50KB en archivos de documentación obsoletos
- ~20KB en scripts antiguos
- ~30KB en archivos de prueba específicos
- ~5KB en middleware obsoleto
- ~100KB en directorio frontend antiguo

### **Beneficios:**
- ✅ Código más limpio y mantenible
- ✅ Documentación más clara y actualizada
- ✅ Menos confusión sobre qué archivos usar
- ✅ Mejor organización del proyecto
- ✅ Reducción de archivos duplicados

---

## ⚠️ **Precauciones**

### **Antes de Eliminar:**
1. Verificar que no hay referencias a los archivos
2. Hacer backup de archivos importantes
3. Confirmar que los archivos son realmente obsoletos

### **Después de Eliminar:**
1. Ejecutar tests completos
2. Verificar despliegue
3. Actualizar documentación si es necesario
