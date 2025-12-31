# SmartSport Scheduler

Sistema de planificación inteligente para centros deportivos que gestiona eventos, recursos y horarios con validación automática de restricciones.

**Versión:** 1.0  
**Desarrollado en:** Python 3.x con Tkinter  
**Estado:** Completo y listo para producción  
**Disponible como:** Código fuente + Ejecutable Windows (.exe)

---

## 🚀 Inicio Rápido

### Para usuarios (sin Python):
1. Descarga `SmartSport Scheduler.exe` de la carpeta `dist/`
2. Doble clic en el archivo
3. ¡Listo para usar!

### Para desarrolladores (con Python):
```bash
git clone https://github.com/tu-usuario/SmartSport-Scheduler.git
cd SmartSport-Scheduler
py main.py
```

---

## Descripción del Proyecto

SmartSport Scheduler es una aplicación de escritorio diseñada para centros deportivos que permite:
- Planificar eventos (partidos, entrenamientos, torneos)
- Gestionar inventario de recursos (canchas, equipamiento deportivo, personal)
- Validar automáticamente conflictos temporales y de recursos
- Aplicar reglas de co-requisitos y exclusiones entre recursos
- Visualizar calendario mensual con disponibilidad de espacios
- Persistencia de datos con escritura atómica en formato JSON
- **Ejecutable independiente** sin necesidad de instalar Python

---

## Características Principales

### Sistema de Validación Multicapa
El planificador valida automáticamente cada evento a través de 4 niveles:

1. **Validación Temporal:**
   - Horario operativo: 7:00 AM - 10:00 PM
   - Detección de solapamiento entre eventos
   - Verificación de fechas válidas

2. **Validación de Recursos:**
   - Existencia en inventario
   - Disponibilidad según eventos concurrentes
   - Cantidad suficiente de recursos simultáneos

3. **Reglas de Co-requisitos (`requires`):**
   - Recursos que deben ir juntos obligatoriamente
   - Ejemplo: "Cancha de Tenis" requiere ["Pelota de Tenis", "Raquetas de Tenis", "Árbitro"]

4. **Reglas de Exclusión (`excludes`):**
   - Recursos incompatibles en el mismo evento
   - Ejemplo: "Piscina Olímpica" excluye ["Sacos de Boxeo", "Estrado de Premiaciones"]

### Interfaz Gráfica Completa
- **Calendario Interactivo:** Vista mensual con indicadores visuales (rojo = ocupado, verde = libre)
- **Gestión de Eventos:** Crear, visualizar, eliminar eventos con diálogos modales
- **Selección de Recursos:** Sistema de diálogos encadenados con validación en cada paso
- **Búsqueda de Slots:** Encuentra automáticamente el próximo horario disponible
- **Persistencia:** Guardar/cargar planificaciones con nombre personalizado

---

## Arquitectura del Sistema

### Estructura del Proyecto
```
SmartSport Scheduler/
├── backend/                  # Lógica de negocio (backend)
│   ├── __init__.py
│   ├── models/               # Modelos de datos
│   │   ├── __init__.py
│   │   ├── exceptions.py     # Excepciones personalizadas
│   │   ├── resource.py       # Clase Resource
│   │   ├── event.py          # Clase Event
│   │   └── planner.py        # Clase Planner (motor de validación)
│   └── utils/                # Utilidades y persistencia
│       ├── __init__.py
│       ├── utils.py          # Utilidades del sistema
│       └── persistence.py    # Funciones de guardado/carga JSON
├── Frontend/                 # Interfaz gráfica (frontend)
│   ├── __init__.py
│   ├── gui.py                # Ventana principal (PlannerGUI)
│   └── dialogs/              # Diálogos modales
│       ├── __init__.py
│       ├── utils_gui.py      # Utilidades GUI (centrado de ventanas)
│       ├── multi_input_dialog.py          # Entrada de fecha/hora
│       ├── resource_selector_dialog.py    # Selector de recursos
│       ├── required_resources_dialog.py   # Notificación co-requisitos
│       └── cuantity_selected_resources.py # Selección de cantidades
├── tests/
│   └── test_planner.py       # Tests unitarios
├── data/                     # Almacenamiento JSON (generado en runtime)
├── main.py                   # Punto de entrada de la aplicación
└── README.md
```

### Ventajas de la Arquitectura Modular

**Separación de Responsabilidades:**
- **backend/models/**: Clases de datos puras sin lógica de presentación
- **backend/utils/**: Funciones utilitarias y persistencia
- **Frontend/dialogs/**: Componentes de UI reutilizables
- **Frontend/gui.py**: Orquestación de la interfaz principal

**Mantenibilidad:**
- Cada clase en su propio archivo facilita navegación y edición
- Imports explícitos mejoran trazabilidad del código
- Modificaciones aisladas sin afectar otros módulos

**Escalabilidad:**
- Agregar nuevos recursos: modificar solo `backend/utils/utils.py`
- Nuevos diálogos: crear archivo en `Frontend/dialogs/`
- Nuevas validaciones: extender `backend/models/planner.py`

**Testabilidad:**
- Módulos independientes facilitan unit testing
- Mock de dependencias más simple
- Tests aislados por funcionalidad

### Backend (`backend/`)

#### Clases Principales

**1. Resource**
```python
@dataclass
class Resource:
    name: str    # Nombre del recurso
    amount: int  # Cantidad total disponible
```
Representa un item del inventario del centro deportivo.

**2. Event**
```python
@dataclass
class Event:
    name: str                          # Nombre del evento
    start: datetime                    # Fecha/hora de inicio
    end: datetime                      # Fecha/hora de fin
    resources: dict[str, Resource]     # Recursos consumidos
```
Representa una actividad programada que consume recursos.

**3. Planner**
```python
@dataclass
class Planner:
    _resources: dict[str, Resource]    # Inventario global
    events: dict[str, Event]           # Eventos programados
    requires: dict[str, list[str]]     # Reglas de co-requisitos
    excludes: dict[str, list[str]]     # Reglas de exclusión
```
Motor principal que gestiona la programación y validación.

#### Métodos Clave del Planner

**`is_valid(start, end, using_resources) -> bool`**
- Valida si un evento puede crearse sin conflictos
- Verifica horarios operativos (7:00-22:00)
- Detecta solapamientos temporales
- Comprueba disponibilidad de recursos
- Aplica reglas `requires` y `excludes`

**`add_events(event: Event) -> None`**
- Agrega un evento si pasa todas las validaciones
- Lanza `DecisionRequired` si el nombre ya existe
- Lanza `ValueError` si la validación falla

**`force_add(event: Event) -> None`**
- Añade evento sin validación (para sobrescrituras confirmadas)

**`remove_event(event_name: str) -> None`**
- Elimina un evento del planificador

**`find_next_slot_step() -> tuple[datetime, datetime] | None`**
- Busca el próximo horario disponible de 1 hora
- Retorna tupla (inicio, fin) o None si no hay slots

**`get_event_list() -> list[dict]`**
- Retorna lista ordenada de eventos como diccionarios
- Útil para serialización y visualización

#### Sistema de Persistencia

**`save_planner(namefile: str, planner: Planner, path: str | None)`**
- Guarda el planificador en formato JSON
- Escritura atómica: usa archivo temporal `.tmp` antes de reemplazar
- Ruta por defecto: `proyecto_root/data/{namefile}.json`

**`load_planner(path: str) -> Planner`**
- Reconstruye un Planner desde archivo JSON
- Deserializa recursos, eventos y reglas

**`planner_to_dict(planner: Planner) -> dict`**
- Serializa un Planner a diccionario
- Convierte datetimes a formato ISO

### Frontend (`Frontend/`)

El frontend está organizado de forma modular con separación de responsabilidades:

#### Ventana Principal (`gui.py`)

**PlannerGUI**
Clase principal que gestiona la ventana de la aplicación.

Elementos principales:
- `events_listbox`: Listbox con todos los eventos programados
- `calendar_frame`: Panel con calendario mensual interactivo
- Botones: Refresh, Add Event, Delete, Save, Load, Find Next Slot, View Details

Funciones destacadas:
- `refresh()`: Actualiza lista de eventos y redibuja calendario
- `add_event_dialog()`: Orquesta el flujo completo de creación de eventos
- `delete_selected()`: Elimina evento seleccionado con confirmación
- `_render_calendar()`: Dibuja calendario con indicadores de ocupación
#### Diálogos Modales (`dialogs/`)

**1. MultiInputDialog** (`multi_input_dialog.py`)
Diálogo modal para capturar fecha/hora (año, mes, día, hora, minutos).

Variables:
- `accepted`: Flag que indica si el usuario confirmó o canceló
- `result`: Tupla (year, month, day, hour, min)

Validación:
- Convierte entradas a enteros
- Muestra error si los datos son inválidos
- ResourceSelectorDialog (`resource_selector_dialog.py`) si la validación es exitosa

**2. ResourceSelectorDialog** (`resource_selector_dialog.py`)
Diálogo para seleccionar recursos de un listbox múltiple.

Flujo:
1. Muestra listbox con todos los recursos disponibles (cantidad > 0)
2. Usuario selecciona múltiples recursos con clic
3. Botón "Agregar recurso(s)" añade selección a lista interna
4. Al presionar "Aceptar", verifica recursos con co-requisitos
5. Si detecta `requires`, abre `RequiredResourcesDialog`
6. Abre `CuantitySelectedResources` para especificar cantidades
7. Retorna diccionario `{nombre_recurso: Resource}`

**3. RequiredResourcesDialog** (`RequiredResourcesDialog`)
Notifica al usuario sobre recursos obligatorios que se agregarán automáticamente.

Comportamiento:
- Muestra mensaje: "Como ha usado el recurso 'X' necesita incluir los recursos obligatorios..."
- Lista recursos requeridos en Listbox
- Al aceptar, agrega recursos faltantes a `result_resources`
- Si se cancela, no continúa el flujo de creación

**4. CuantitySelectedResources** (`cuantity_selected_resources.py`)
Diálogo dinámico que ajusta su tamaño según cantidad de recursos.

Características:
- Muestra tabla con columnas: Recurso | Cantidad disponible | Cantidad a usar
- Spinbox para recursos con amount > 1
- Geometría dinámica usando `update_idletasks()` y `winfo_reqwidth/height()`
- Valida que cantidades sean válidas antes de cerrar
- Retorna diccionario `{nombre: Resource(nombre, cantidad)}`

**5. Utils_Gui** (`utils_gui.py`)
Clase utilitaria con método `center_window(window)` para centrar ventanas en pantalla.

#### Flujo de Creación de Eventos

1. Usuario hace clic en "Add Event"
2. `add_event_dialog()` solicita:
   - Nombre del evento (simpledialog)
   - Fecha/hora inicio (`MultiInputDialog`)
   - Fecha/hora fin (`MultiInputDialog`)
   - Recursos (`ResourceSelectorDialog` → `RequiredResourcesDialog` → `CuantitySelectedResources`)
3. Valida que todos los diálogos hayan sido aceptados (flags `accepted_s`, `accepted_e`, `accepted_r`)
4. Llama a `planner.add_events(event)`
5. Maneja excepciones:
   - `ValueError`: Muestra error de validación
   - `DecisionRequired`: Pregunta si sobrescribir evento existente
6. Si usuario confirma sobrescritura, llama a `planner.force_add(event)`
7. Refresca interfaz con `refresh()`

#### Sistema de Flags de Cancelación

Todos los diálogos implementan flag `accepted` que permite:
- Cancelar flujo en cualquier punto cerrando ventana
- Validar que usuario completó el paso antes de continuar
- Evitar creación de eventos incompletos

Ejemplo de verificación:
```python
if all((accepted_s, accepted_e, accepted_r)):
    # Solo procede si todos los diálogos fueron aceptados
    self.planner.add_events(event)
```

---

## Inventario de Recursos Predefinidos

El sistema viene con 50+ recursos configurados para un centro deportivo completo:

### Espacios (cantidad: 1 cada uno)
- Canchas: Football, Tenis, Basket (techada/aire libre), FootSal, Voleibol, Badminton, Squash
- Instalaciones: Piscina Olímpica, Estadio Baseball, Ring de Boxeo, Pista de Carreras
- Habitaciones: Juegos de Mesa, Habitación con Colchón, Biosaludable

### Implementos Deportivos (cantidad variable)
- Pelotas: Football (15), Tenis (50), Basket (15), Baseball (30), etc.
- Raquetas: Tenis (6), Badminton (6), Tenis de Mesa (6), Squash (6)
- Equipamiento: Bates (30), Guantes (30), Protectores (30), Cascos (30)
- Otros: Boyas (16), Sacos de Boxeo (4), Mesas PingPong (8), Tableros Ajedrez (8)

### Personal (cantidad limitada)
- Árbitros (5)
- Personal de Primeros Auxilios (5)
- Salvavidas (16)
- Comentaristas (6)
- Ambulancias (2)

---

## Requisitos del Sistema

### Para ejecutar desde código fuente:
- **Python:** 3.10 o superior
- **Dependencias:** Solo bibliotecas estándar de Python
  - `tkinter` (incluido con Python en Windows/macOS)
  - `dataclasses`, `datetime`, `json`, `pathlib`
- **Sistema Operativo:** Windows, macOS, Linux

### Para usar el ejecutable (.exe):
- **Python:** NO requerido
- **Sistema Operativo:** Windows 7, 8, 10, 11
- **Espacio en disco:** ~15 MB (10 MB exe + 5 MB datos)
- **RAM:** Mínimo 100 MB
- **Permisos:** Puede requerir aprobación de Windows Defender en primera ejecución

---

## Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/SmartSport-Scheduler.git
cd SmartSport-Scheduler
```

### 2. Ejecutar la aplicación

#### Opción A: Desde código fuente (requiere Python)
```bash
# Windows
py main.py

# Linux/macOS
python3 main.py
```

#### Opción B: Ejecutable (.exe) - Solo Windows
Si prefieres un ejecutable independiente sin necesidad de Python:


## 🚀 Descarga

**Ejecutable Windows (.exe):**  
[Descargar última versión](https://github.com/AtlasOffMind/SmartSport-Scheduler/releases/latest)

**Ejecutar:**
- Doble clic en el archivo `.exe`
- No requiere instalación de Python
- Compatible con Windows 7, 8, 10, 11

**Primera ejecución:**
- Puede tardar unos segundos en iniciar
- Si Windows Defender lo bloquea: "Más información" → "Ejecutar de todos modos"

### 3. Generar tu propio ejecutable (.exe)

Si modificas el código y quieres generar un nuevo .exe:

```bash
# Instalar PyInstaller (solo una vez)
pip install pyinstaller

# Generar ejecutable
pyinstaller --onefile --windowed --name "SmartSport Scheduler" main.py
```

El ejecutable estará en `dist/SmartSport Scheduler.exe` (~10 MB)

**Opciones de PyInstaller:**
- `--onefile`: Genera un único archivo .exe
- `--windowed`: Oculta la consola (solo GUI)
- `--name`: Nombre personalizado del ejecutable
- `--icon=icon.ico`: Agregar ícono personalizado (opcional)

**Para incluir archivos adicionales:**
```bash
pyinstaller --onefile --windowed --name "SmartSport Scheduler" --add-data "data;data" main.py
```

**Distribución del .exe:**
- Copia solo el archivo `.exe` de la carpeta `dist/`
- (Opcional) Incluye carpeta `data/` si hay planificaciones guardadas
- El receptor NO necesita tener Python instalado
- Tamaño: ~10 MB (incluye Python y dependencias)

---

## Guía de Uso

### Crear un Evento

1. Clic en **"Add Event"**
2. Ingresar nombre del evento
3. Seleccionar fecha/hora de inicio (año, mes, día, hora, minutos)
4. Seleccionar fecha/hora de fin
5. Seleccionar recursos necesarios del listbox
6. Clic en **"Agregar recurso(s)"** y luego **"Aceptar"**
7. Si aparece diálogo de recursos obligatorios, confirmar con **"Aceptar"**
8. Especificar cantidades en los Spinbox (si aplica)
9. Confirmar creación

Si el evento ya existe, se preguntará si desea sobrescribirlo.

### Ver Eventos de un Día

1. En el calendario, hacer clic en un día (botón del número)
2. Aparece ventana con lista de eventos en ese día
3. Días rojos = tienen eventos | Días verdes = libres

### Eliminar un Evento

1. Seleccionar evento en la lista
2. Clic en **"Delete Event"**
3. Confirmar eliminación

### Guardar Planificación

1. Clic en **"Save"**
2. Ingresar nombre de archivo (sin extensión .json)
3. Archivo se guarda en `data/{nombre}.json`

### Cargar Planificación

1. Clic en **"Load Planner"**
2. Navegar y seleccionar archivo `.json`
3. Planificador se reemplaza con datos cargados

### Buscar Próximo Slot Disponible

1. Clic en **"Find Next Slot"**
2. Sistema busca próximo horario libre de 1 hora
3. Muestra fecha/hora inicio y fin

### Ver Detalles de un Evento

1. Seleccionar evento en la lista
2. Clic en **"View Details"**
3. Ventana muestra nombre, horarios y recursos utilizados

---

## Estructura de Datos JSON

Ejemplo de archivo guardado:
```json
{
  "resources": {
    "Cancha de Tenis": {"name": "Cancha de Tenis", "amount": 1},
    "Pelota de Tenis": {"name": "Pelota de Tenis", "amount": 50}
  },
  "events": {
    "Torneo de Tenis": {
      "name": "Torneo de Tenis",
      "start": "2025-12-31T10:00:00",
      "end": "2025-12-31T12:00:00",
      "resources": {
        "Cancha de Tenis": 1,
        "Pelota de Tenis": 3,
        "Raquetas de Tenis": 2,
        "Arbitro": 1
      }
    }
  },
  "requires": { ... },
  "excludes": { ... }
}

```

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'backend'"
**Causa:** Python no encuentra los módulos del proyecto  
**Solución:** Ejecutar siempre desde la raíz del proyecto con `py main.py`  
**Alternativa:** Verificar que `__init__.py` existe en `backend/` y `Frontend/`

### Evento válido se rechaza
**Verificar:**
- Horario entre 7:00 AM y 10:00 PM
- No solapa con eventos existentes
- Todos los co-requisitos están incluidos
- No hay recursos excluidos juntos
- Cantidad de recursos no excede disponibilidad

### Diálogo se cierra sin guardar
**Causa:** Usuario cerró ventana en lugar de presionar "Aceptar"  
**Comportamiento esperado:** El flujo se cancela y vuelve a ventana principal

### Ejecutable (.exe) bloqueado por Windows Defender
**Causa:** Windows marca ejecutables desconocidos como potencialmente peligrosos  
**Solución:**
1. Hacer clic en "Más información"
2. Seleccionar "Ejecutar de todos modos"
3. (Opcional) Agregar excepción en Windows Defender para `SmartSport Scheduler.exe`

**Nota:** Es un falso positivo común en ejecutables creados con PyInstaller

### El .exe tarda mucho en iniciar
**Causa normal:** Primera ejecución (antivirus escaneando)  
**Solución:** Esperar ~5-10 segundos. Ejecuciones posteriores serán más rápidas

### Error al generar .exe con PyInstaller
**Verificar:**
- PyInstaller instalado: `pip install pyinstaller`
- Ejecutar desde raíz del proyecto
- No tener el .exe anterior abierto
- Cerrar todas las instancias de la aplicación

---

## Créditos

**Desarrollado por:** Gerardo Javier Pujol Suarez 
**Año:** 2025  

---

## Contacto

Para reportar bugs o sugerencias:
- **GitHub Issues:** [\[AtlasOffMind\]](https://github.com/AtlasOffMind/SmartSport-Scheduler)
- **Email:** gameover.mg533@gmail.com

---


