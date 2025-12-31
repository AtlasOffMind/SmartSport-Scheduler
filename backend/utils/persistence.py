import json
from pathlib import Path
from datetime import datetime
from backend import Planner, Resource, Event


def planner_to_dict(planner: Planner):
    """Convierte un Planner a diccionario para serialización"""
    return {
        "resources": {
            name: {"name": r.name, "amount": r.amount}
            for name, r in planner._resources.items()
        },
        "events": {
            name: {
                "name": ev.name,
                "start": ev.start.isoformat(),
                "end": ev.end.isoformat(),
                "resources": {rn: r.amount for rn, r in ev.resources.items()},
            }
            for name, ev in planner.events.items()
        },
        "requires": planner.requires,
        "excludes": planner.excludes,
    }

def save_planner(namefile: str, planner: Planner, path: str | None = None):
    """Guarda el planner en un archivo JSON de forma atómica"""
    if path is None:
        p = get_default_data_path(namefile)
    else:
        p = Path(path)
    data = planner_to_dict(planner)
    tmp = p.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(p)  # escritura atómica

def load_planner(path: str | None = None) -> Planner:
    """Carga un planner desde un archivo JSON"""
    p = Path(path)

    with p.open("r", encoding="utf-8") as f:
        data: dict = json.load(f)
    # reconstruir Planner
    pl = Planner({})
    # resources
    pl._resources = {
        name: Resource(d["name"], int(d["amount"]))
        for name, d in data.get("resources", {}).items()
    }
    # events
    for ename, ed in data.get("events", {}).items():
        ev_resources = {
            rn: Resource(rn, int(amount))
            for rn, amount in ed.get("resources", {}).items()
        }
        ev = Event(
            name=ed["name"],
            start=datetime.fromisoformat(ed["start"]),
            end=datetime.fromisoformat(ed["end"]),
            resources=ev_resources,
        )
        pl.events[ename] = ev
    pl.requires = data.get("requires", {})
    pl.excludes = data.get("excludes", {})
    return pl

def get_default_data_path(namefile: str) -> Path:
    """Obtiene la ruta por defecto para guardar datos (carpeta /data del proyecto)"""
    # Guardar en la carpeta del proyecto
    project_root = Path(__file__).resolve().parent.parent.parent
    folder = project_root / "data"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{namefile}.json"
