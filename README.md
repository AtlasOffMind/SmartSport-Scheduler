# SmartSport Scheduler

Sistema de planificación inteligente para centros deportivos que gestiona eventos, recursos y horarios con validación automática de restricciones.

**Versión:** 1.0  
**Desarrollado en:** Python 3.x con Tkinter  
**Estado:** Completo y listo para producción

---

## Descripción del Proyecto

SmartSport Scheduler es una aplicación de escritorio diseñada para centros deportivos que permite:
- Planificar eventos (partidos, entrenamientos, torneos)
- Gestionar inventario de recursos (canchas, equipamiento deportivo, personal)
- Validar automáticamente conflictos temporales y de recursos
- Aplicar reglas de co-requisitos y exclusiones entre recursos
- Visualizar calendario mensual con disponibilidad de espacios
- La persistencia de datos con escritura atómica en formato JSON

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
├── Scripts/
│   └── Proyecto.py          # Backend: lógica de negocio y persistencia
├── frontend/
│   └── gui.py               # Interfaz gráfica Tkinter
├── tests/
│   └── test_planner.py      # Tests unitarios
├── data/                     # Almacenamiento JSON (generado en runtime)
└── README.md
```

### Backend (`Scripts/Proyecto.py`)

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

### Frontend (`frontend/gui.py`)

#### Componentes de Interfaz

**1. PlannerGUI**
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
- `_on_day_click(date)`: Muestra eventos del día seleccionado

**2. MultiInputDialog**
Diálogo modal para capturar fecha/hora (año, mes, día, hora, minutos).

Variables:
- `accepted`: Flag que indica si el usuario confirmó o canceló
- `result`: Tupla (year, month, day, hour, min)

Validación:
- Convierte entradas a enteros
- Muestra error si los datos son inválidos
- Solo marca `accepted=True` si la validación es exitosa

**3. ResourceSelectorDialog**
Diálogo para seleccionar recursos de un listbox múltiple.

Flujo:
1. Muestra listbox con todos los recursos disponibles (cantidad > 0)
2. Usuario selecciona múltiples recursos con clic
3. Botón "Agregar recurso(s)" añade selección a lista interna
4. Al presionar "Aceptar", verifica recursos con co-requisitos
5. Si detecta `requires`, abre `RequiredResourcesDialog`
6. Abre `CuantitySelectedResources` para especificar cantidades
7. Retorna diccionario `{nombre_recurso: Resource}`

**4. RequiredResourcesDialog**
Notifica al usuario sobre recursos obligatorios que se agregarán automáticamente.

Comportamiento:
- Muestra mensaje: "Como ha usado el recurso 'X' necesita incluir los recursos obligatorios..."
- Lista recursos requeridos en Listbox
- Al aceptar, agrega recursos faltantes a `result_resources`
- Si se cancela, no continúa el flujo de creación

**5. CuantitySelectedResources**
Diálogo dinámico que ajusta su tamaño según cantidad de recursos.

Características:
- Muestra tabla con columnas: Recurso | Cantidad disponible | Cantidad a usar
- Spinbox para recursos con amount > 1
- Geometría dinámica usando `update_idletasks()` y `winfo_reqwidth/height()`
- Valida que cantidades sean válidas antes de cerrar
- Retorna diccionario `{nombre: Resource(nombre, cantidad)}`

**6. Utils_Gui**
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

- **Python:** 3.10 o superior
- **Dependencias:** Solo bibliotecas estándar de Python
  - `tkinter` (incluido con Python en Windows/macOS)
  - `dataclasses`, `datetime`, `json`, `pathlib`
- **Sistema Operativo:** Windows, macOS, Linux

---

## Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/SmartSport-Scheduler.git
cd SmartSport-Scheduler
```

### 2. Ejecutar la aplicación
```bash
# Windows
py -3 frontend/gui.py

# Linux/macOS
python3 frontend/gui.py
```

### 3. Ejecutar tests
```bash
# Desde la raíz del proyecto
python -m unittest discover -s tests
```

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

### Error: "Import Proyecto could not be resolved"
**Causa:** El LSP del editor no encuentra el módulo  
**Impacto:** Solo afecta editor, no runtime  
**Solución:** Ignorar advertencia o crear `__init__.py` en `Scripts/`

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

---

## Créditos

**Desarrollado por:** Gerardo Javier Pujol Suarez 
**Año:** 2025  

---

## Contacto

Para reportar bugs o sugerencias:
- **GitHub Issues:** [\[AtlasOffMind\]](https://github.com/AtlasOffMind/SmartSport-Scheduler)
- **Email:** gameover.mg533@gmail.com
