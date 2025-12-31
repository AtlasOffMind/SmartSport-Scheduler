# SmartSport Scheduler - Ejecutable

## ✅ Ejecutable generado exitosamente

**Ubicación:** `dist/SmartSport Scheduler.exe`  
**Tamaño:** ~10 MB  
**Versión:** 1.0

---

## 🚀 Cómo ejecutar

### Opción 1: Doble clic
Simplemente haz doble clic en `SmartSport Scheduler.exe`

### Opción 2: Desde línea de comandos
```bash
cd dist
"SmartSport Scheduler.exe"
```

---

## 📦 Distribución

Para distribuir la aplicación a otros usuarios:

1. **Copiar el archivo:**
   - `dist/SmartSport Scheduler.exe` (ejecutable principal)

2. **(Opcional) Incluir carpeta de datos:**
   - Si tienes planificaciones guardadas, copia también la carpeta `data/`
   - Colocarla en el mismo directorio que el .exe

3. **Compartir:**
   - No requiere instalación de Python
   - Compatible con Windows 7, 8, 10, 11
   - No necesita dependencias adicionales

---

## ⚠️ Notas importantes

### Primera ejecución
- Puede tardar unos segundos en iniciar (normal)
- Algunos antivirus pueden escanearlo (falso positivo)
- Si Windows Defender lo bloquea:
  - Clic en "Más información"
  - Seleccionar "Ejecutar de todos modos"

### Persistencia de datos
- Los archivos `.json` se guardan en la carpeta `data/`
- La carpeta `data/` se crea automáticamente en el mismo directorio del .exe
- Para respaldar tus datos, copia la carpeta `data/`

### Limitaciones
- El .exe es portátil pero grande (~10 MB) porque incluye Python
- Solo funciona en Windows (para otros OS usar Python directamente)

---

## 🔧 Regenerar el ejecutable

Si modificas el código fuente, regenera el .exe con:

```bash
cd "c:\My things\Git\SmartSport Scheduler"
pyinstaller --onefile --windowed --name "SmartSport Scheduler" main.py
```

El nuevo ejecutable estará en `dist/SmartSport Scheduler.exe`

---

## 📝 Archivos generados por PyInstaller

Después de ejecutar PyInstaller, se crean:

- **`dist/`** - Contiene el ejecutable final
- **`build/`** - Archivos temporales de compilación (se puede borrar)
- **`SmartSport Scheduler.spec`** - Configuración de PyInstaller (se puede borrar)

Solo necesitas mantener la carpeta `dist/` con el ejecutable.

---