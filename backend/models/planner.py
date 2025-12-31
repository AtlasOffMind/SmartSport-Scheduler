from dataclasses import dataclass, field
from datetime import datetime, timedelta
from .resource import Resource
from .event import Event
from .exceptions import DecisionRequired


@dataclass
class Planner:
    """Motor de planificación que gestiona eventos y recursos"""

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
