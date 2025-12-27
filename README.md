# SmartSport Scheduler — borrador

Estado: backend básico implementado (modelo de datos, validación, persistencia JSON).

Dominio
- Centro deportivo: eventos (partidos, entrenamientos) que consumen recursos (canchas, pelotas, árbitros, etc.).

Arquitectura (actual)
- `Scripts/Proyecto.py` contiene las implementaciones principales:
  - `Resource`, `Event`, `Planner` dataclasses
  - Reglas `requires` y `excludes` preconfiguradas
  - Funciones: `planner_to_dict`, `save_planner`, `load_planner`, `get_default_data_path`
  - Un planner por defecto `p` con recursos de ejemplo y algunos eventos de demostración

Persistencia
- Los datos se guardan en `data/planner.json` (ruta por defecto del proyecto).
- Escritura atómica: se escribe en un `.tmp` y luego se reemplaza.

Tests
- Se añadió `tests/test_planner.py` con pruebas básicas de:
  - guardado y carga (roundtrip)
  - detección de conflictos entre eventos
  - enforcement de reglas `requires`

Cómo ejecutar
1. Ejecutar los tests (desde la raíz del proyecto):
```bash
python -m unittest discover -s tests
```

2. Ejecutar el script principal (ejemplo):
```bash
py -3 Scripts/Proyecto.py
```
