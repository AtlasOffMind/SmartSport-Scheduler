from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pprint import pprint
import os

# import uuid
# uuid.uuid4()


@dataclass
class DecisionRequired(Exception):
    message: str = ""

    def __str__(self):
        return self.message


# Recursos
@dataclass
class Resource:
    name: str
    amount: int


# Eventos
@dataclass
class Event:
    name: str
    start: datetime
    end: datetime
    resources: dict[str, Resource]


# Planificador
@dataclass
class Planner:
    # Estos son los recursos globales
    _resources: dict[str, Resource] = field(default_factory=dict)
    # Estos son los eventos globales
    events: dict[str, Event] = field(default_factory=dict)

    # Reglas de restricciones (co-requisitos y exclusiones) - valores por defecto
    requires: dict[str, list[str]] = field(
        default_factory=lambda: {
            # Espacios que requieren personal o equipos
            "Cancha de Football": [
                "Arbitro",
                "Pelota de Football",
                "Personal de primeros auxilios",
            ],
            "Cancha de FootSal": [
                "Arbitro",
                "Pelota de Footsal",
                "Personal de primeros auxilios",
            ],
            "Cancha de Basket (techada)": ["Pelota de Basket", "Arbitro"],
            "Cancha de Basket (aire libre)": ["Pelota de Basket", "Arbitro"],
            "Piscina Olimpica": ["Salva Vidas", "Personal de primeros auxilios"],
            "Estadio de BaseBall": [
                "Arbitro",
                "Personal de primeros auxilios",
                "Comentaristas",
                "Pelota de Baseball",
                "Bates de BaseBall",
                "Guantes de BaseBall",
                "Protectores de BaseBall",
            ],
            "Cancha de Boleyball": [
                "Arbitro",
                "Pelota de Boleyball",
                "Personal de primeros auxilios",
            ],
            "Cancha de Badmintong": [
                "Arbitro",
                "Pelota de Badmintong",
                "Raquetas de Badmintong",
                "Personal de primeros auxilios",
            ],
            "Cancha de Cancha": [
                "Arbitro",
                "Pelota de Cancha",
                "Raquetas de Cancha",
                "Personal de primeros auxilios",
            ],
            "Ring de boxeo": [
                "Arbitro",
                "Guantes de Boxeo",
                "Cascos de Boxeo",
                "Personal de primeros auxilios",
            ],
            "Cancha de Tenis": ["Pelota de Tenis", "Raquetas de Tenis", "Arbitro"],
            # Implementos que requieren espacio y/o equipos complementarios
            "Pelota de Football": ["Cancha de Football"],
            "Pelota de Footsall": ["Cancha de FootSal"],
            "Pelota de Tenis": ["Cancha de Tenis", "Raquetas de Tenis"],
            "Mesa de PingPong": [
                "Raquetas de Tenis de Mesa",
                "Pelota de Tenis de Mesa",
                "Ned de Tenis de Mesa",
                "Habitacion para juegos de mesa",
            ],
            # Protección personal que suele acompañar entrenamientos de contacto
            "Cascos de Karate": ["Protectores de Karate", "Habitacion con Colchon"],
            "Cascos de Taekwando": [
                "Protectores de Taekwando",
                "Habitacion con Colchon",
            ],
            "Sacos de Boxeo": ["Guantes de Boxeo", "Cascos de Boxeo"],
        }
    )

    excludes: dict[str, list[str]] = field(
        default_factory=lambda: {
            # Recursos que no deberían coexistir en el mismo evento (incompatibilidades)
            "Piscina Olimpica": ["Sacos de Boxeo", "Estrado de Premiaciones"],
            # Cascos/Protectores de distintas disciplinas no deberían mezclarse
            "Cascos de Karate": [
                "Cascos de Taekwando",
                "Cascos de Boxeo",
                "Guantes de Boxeo",
            ],
            "Cascos de Taekwando": [
                "Cascos de Karate",
                "Cascos de Boxeo",
                "Guantes de Boxeo",
            ],
            "Protectores de Taekwando": [
                "Protectores de Karate",
                "Cascos de Boxeo",
                "Guantes de Boxeo",
            ],
            "Protectores de Karate": [
                "Protectores de Taekwando",
                "Cascos de Boxeo",
                "Guantes de Boxeo",
            ],
            "Cascos de Boxeo": [
                "Protectores de Taekwando",
                "Cascos de Taekwando",
                "Cascos de Karate",
                "Protectores de Taekwando",
                "Protectores de Karate",
            ],
        }
    )

    # region Metodos de la clase Planner
    # Determinar si el evento es valido
    def is_valid(
        self,
        start: datetime,
        end: datetime,
        using_resources: dict[str, Resource] | None = None,
    ) -> bool:

        day_start: datetime = datetime(start.year, start.month, start.day, 7, 0)
        day_end: datetime = datetime(start.year, start.month, start.day, 22, 0)

        if using_resources is None:
            return False

        if not isinstance(start, datetime) or not isinstance(end, datetime):
            return False
        if start >= end:
            return False
        if start < day_start:
            return False
        if end > day_end:
            return False

        for name in using_resources.keys():
            # existencia del recurso en el inventario
            if name not in self._resources:
                return False

            # verificacion de los co-requisitos
            for req in self.requires.get(name, []):
                if req not in using_resources:
                    return False

            # verificacion de las exclusiones
            for ex in self.excludes.get(name, []):
                if ex in using_resources:
                    return False

        # Calcular uso actual por recurso en eventos que se solapan con (start,end)
        used: dict[str, int] = {}
        for ev in self.events.values():
            if not (ev.end <= start or ev.start >= end):
                for rname, r in ev.resources.items():
                    used[rname] = used.get(rname, 0) + r.amount

        # Verificar que para cada recurso solicitado, la suma (usado + solicitado) <= inventario
        for name, req in using_resources.items():
            req_amount = req.amount
            avail = self._resources.get(name).amount
            already = used.get(name, 0)
            if already + req_amount > avail:
                return False

        return True

    # Añadir eventos
    def add_events(self, event: Event) -> None:
        if self.events.get(event.name):
            raise DecisionRequired("This event already exist")
        
        if self.is_valid(event.start, event.end, event.resources):
                self.events[event.name] = event
        else:
            raise ValueError("That's not a valid event")

    def force_add(self, event: Event) -> None:
        self.events[event.name] = event

    # Remover eventos
    def remove_event(self, event_name):
        if self.events.get(event_name):
            del self.events[event_name]
        else:
            raise Exception(f"This event:'{event_name}' dosen't exist")

    # Ver detalles
    def see_details(self, event_name):
        return self.events.get(event_name)
        # if self.events.get(event_name):
        #     print(f"Name of the event : {event_name}")
        #     print(
        #         f"Date of the event : start: {self.events[event_name].start} \r\n
        #                               end: {self.events[event_name].end}"
        #     )

        #     print("Resources details: ")
        #     for r in self.events[event_name].resources.values():
        #         print(f"  {r.name}  =>  {r.amount}")
        # else:
        #     print("That Event dosen't exist")

    # Obtener listado organizado
    def get_event_list(self) -> list[dict[str,]]:
        result = []
        for key, ev in self.events.items():
            resources = [
                {"name": rn, "amount": r.amount} for rn, r in ev.resources.items()
            ]
            result.append(
                {
                    "key": key,
                    "name": ev.name,
                    "start": ev.start,
                    "end": ev.end,
                    "resources": resources,
                }
            )

        self.sort_by_date(result)
        return result

    # Metodo de ordenacion por datetime
    def sort_by_date(self, lst: list[dict[str,]]):
        lst.sort(key=lambda e: e["start"])

    def sort_events(self):
        ev_dict = self.events
        ev_dict = sorted(ev_dict.values(), key=lambda x: x.start)
        self.events.clear()
        for e in ev_dict:
            self.events[e.name] = e

    # Metodo para hacer una tabla bonita para la consola
    def events_table(self) -> str:
        rows = []
        for ev in self.get_event_list():
            res_lines = [f"{r['name']} ({r['amount']})" for r in ev["resources"]]
            res_cell = "\n".join(res_lines) if res_lines else "-"
            rows.append(
                [ev["name"], ev["start"].isoformat(), ev["end"].isoformat(), res_cell]
            )

        headers = ["Evento", "Start", "End", "Recursos (nombre (cantidad))"]

        # calcular anchos
        cols = list(zip(*([headers] + rows)))
        widths = [max(len(str(cell)) for cell in col) for col in cols]

        lines = []

        # header
        lines.append(" | ".join(h.ljust(w) for h, w in zip(headers, widths)))
        lines.append("-+-".join("-" * w for w in widths))

        # filas (soportan celdas multilinea)
        for row in rows:
            # dividir por líneas y alinear por filas
            cell_lines = [str(c).splitlines() for c in row]
            max_lines = max(len(cl) for cl in cell_lines)
            for i in range(max_lines):
                parts = [
                    (cl[i] if i < len(cl) else "").ljust(w)
                    for cl, w in zip(cell_lines, widths)
                ]
                lines.append(" | ".join(parts))
            lines.append("-+-".join("-" * w for w in widths))
        return "\n".join(lines)

    # Obtener disponibilidad
    def find_next_slot_step(self) -> tuple[datetime, datetime] | None:

        start_point: datetime = datetime(2025, 12, 28, 10, 0)
        duration: timedelta = timedelta(hours=1)
        day_start: datetime = datetime(
            start_point.year, start_point.month, start_point.day, 7, 0
        )

        # Determinar punto de inicio respetando horario operativo
        start_point = max(start_point, day_start)
        day = day_start.date()

        # Obtener eventos del día (ya están ordenados por start)
        today_events = [ev for ev in self.events.values() if ev.start.date() == day]

        # Iterar por eventos del día
        for event in today_events:
            gap_duration = event.start - start_point

            # Si hay espacio suficiente antes del evento, retornar ese slot
            if gap_duration >= duration:
                return (start_point, start_point + gap_duration)

            # Avanzar el punto de inicio al final del evento
            start_point = max(start_point, event.end)

        # Verificar si hay espacio después del último evento
        end_point = start_point + duration
        day_end: datetime = datetime(
            start_point.year, start_point.month, start_point.day, 22, 0
        )

        # TODO revisar esto para el caso en q al final no se pueda el evento xq este cerrado el dominio
        if end_point <= day_end:
            return (start_point, end_point)
        else:
            end_point += timedelta(1) - (end_point - day_start - duration)

        return None

    # endregion


@dataclass
class Utils:
    def create_planner():
        raw_global_resources = {
            #                               Espacios
            "Cancha de Football": Resource("Cancha de Football", 1),
            "Cancha de Tenis": Resource("Cancha de Tenis", 1),
            "Cancha de Basket (techada)": Resource("Cancha de Basket (techada)", 1),
            "Cancha de Basket (aire libre)": Resource(
                "Cancha de Basket (aire libre)", 1
            ),
            "Cancha de FootSal": Resource("Cancha de FootSal", 1),
            "Cancha de Boleyball": Resource("Cancha de Boleyball", 1),
            "Cancha de Badmintong": Resource("Cancha de Badmintong", 1),
            "Cancha de Cancha": Resource("Cancha de Cancha", 1),
            "Piscina Olimpica": Resource("Piscina Olimpica", 1),
            "Habitacion para juegos de mesa": Resource(
                "Habitacion para juegos de mesa", 1
            ),
            "Habitacion con Colchon": Resource("Habitacion con Colchon", 1),
            "Pista de Carreras": Resource("Pista de Carreras", 1),
            "Biosaludable (techado)": Resource("Biosaludable (techado)", 1),
            "Biosaludable (aire libre)": Resource("Biosaludable (aire libre)", 1),
            "Estadio de BaseBall": Resource("Estadio de BaseBall", 1),
            "Ring de boxeo": Resource("Estadio de BaseBall", 1),
            #                             Implementos
            "Pelota de Football": Resource("Pelota de Football", 15),
            "Pelota de Footsal": Resource("Pelota de Footsal", 15),
            "Pelota de Tenis": Resource("Pelota de Tenis", 50),
            "Pelota de Tenis de Mesa": Resource("Pelota de Tenis de Mesa", 50),
            "Pelota de Boleyball": Resource("Pelota de Boleyball", 15),
            "Pelota de Basket": Resource("Pelota de Basket", 15),
            "Pelota de Cancha": Resource("Pelota de Cancha", 15),
            "Pelota de Badmintong": Resource("Pelota de Badmintong", 15),
            "Pelota de Baseball": Resource("Pelota de Baseball", 30),
            "Raquetas de Cancha": Resource("Raquetas de Cancha", 6),
            "Raquetas de Badmintong": Resource("Raquetas de Badmintong", 6),
            "Raquetas de Tenis": Resource("Raquetas de Tenis", 6),
            "Raquetas de Tenis de Mesa": Resource("Raquetas de Tenis de Mesa", 6),
            "Bates de BaseBall": Resource("Bates de BaseBall", 30),
            "Guantes de BaseBall": Resource("Guantes de BaseBall", 30),
            "Guantes de Boxeo": Resource("Guantes de Boxeo", 30),
            "Protectores de BaseBall": Resource("Protectores de BaseBall", 30),
            "Cascos de BaseBall": Resource("Cascos de BaseBall", 30),
            "Cascos de Boxeo": Resource("Cascos de Boxeo", 30),
            "Protectores de Karate": Resource("Protectores de Karate", 30),
            "Cascos de Karate": Resource("Cascos de Karate", 30),
            "Protectores de Taekwando": Resource("Protectores de Taekwando", 30),
            "Cascos de Taekwando": Resource("Cascos de Taekwando", 30),
            "Boyas": Resource("Boyas", 16),
            "Sacos de Boxeo": Resource("Sacos de Boxeo", 4),
            "Estrado de Premiaciones": Resource("Estrado de Premiaciones", 4),
            "Altavoces": Resource("Altavoces", 16),
            "Microfonos": Resource("Microfonos", 8),
            "Mesa de PingPong": Resource("Mesa de PingPong", 8),
            "Tablero de ajedrez": Resource("Tablero de ajedrez", 8),
            #                               Personal
            "Arbitro": Resource("Arbitro", 5),
            "Personal de primeros auxilios": Resource(
                "Personal de primeros auxilios", 5
            ),
            "Salva Vidas": Resource("Salva Vidas", 16),
            "Ambulacia": Resource("Ambulacia", 2),
            "Comentaristas": Resource("Comentaristas", 6),
        }
        return Planner(raw_global_resources, {})


# region Casos de prueba
# raw_actual_rfootbal = [
#     ("Cancha de Football", 1),
#     ("Pelota de Football", 3),
#     ("Arbitro", 1),
#     ("Personal de primeros auxilios", 2),
# ]
# raw_actual_rfootbal = {
#     name: Resource(name, amount) for name, amount in raw_actual_rfootbal
# }

# raw_actual_rfootsal = [
#     ("Cancha de FootSal", 1),
#     ("Pelota de Footsal", 3),
#     ("Arbitro", 1),
#     ("Personal de primeros auxilios", 2),
# ]
# raw_actual_rfootsal = {
#     name: Resource(name, amount) for name, amount in raw_actual_rfootsal
# }

# raw_actual_rBasket_t = [
#     ("Cancha de Basket (techada)", 1),
#     ("Pelota de Basket", 3),
#     ("Arbitro", 1),
# ]
# raw_actual_rBasket_t = {
#     name: Resource(name, amount) for name, amount in raw_actual_rBasket_t
# }

# e = Event(
#     "Partido de Football",
#     datetime(2025, 5, 7, 10, 0),
#     datetime(2025, 5, 7, 12, 0),
#     raw_actual_rfootbal,
# )
# b = Event(
#     "Partido de Footsal",
#     datetime(2025, 5, 7, 19, 0),
#     datetime(2025, 5, 7, 20, 0),
#     raw_actual_rfootsal,
# )
# c = Event(
#     "Partido de Basket",
#     datetime(2025, 5, 9, 15, 0),
#     datetime(2025, 5, 9, 16, 0),
#     raw_actual_rBasket_t,
# )

# print(p.events_table())

# p.add_events(b)
# p.add_events(e)
# p.add_events(c)
# p.sort_events()

# print(p.events_table())

# pprint(p._resources)
# p.remove_events("Partido de Footsal")
# pprint(p._resources)

# print(p.events_table())

# p.see_details("Partido de Football")
# p.see_details("Partido de Footsall")


# # print(
# #     p.find_next_slot_step(
# #         timedelta(0, 60 * 60),
# #         datetime(2025, 5, 7, 10, 0),
# #         {},
# #     )
# # )

# resta = datetime(2025, 5, 8, 10, 0) - datetime(2025, 5, 7, 10, 0)
# print(resta)

# endregion


import json
from pathlib import Path
from datetime import datetime


def planner_to_dict(planner: Planner):
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


def save_planner(namefile: str, planner, path: str | None = None):
    if path is None:
        p = get_default_data_path(namefile)
    else:
        p = Path(path)
    data = planner_to_dict(planner)
    tmp = p.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(p)  # escritura atómica


def load_planner(path: str | None = None):
    p = Path(path)

    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
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
    # Guardar en la carpeta del proyecto
    project_root = Path(__file__).resolve().parent.parent
    folder = project_root / "data"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{namefile}.json"
