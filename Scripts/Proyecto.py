from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, time
from typing import Dict


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

#Planificador
@dataclass
class Planner:
    # Estos son los recursos globales
    resources: dict[str, Resource] = field(default_factory=dict)
    # Estos son los eventos globales
    events: dict[str, Event] = field(default_factory=dict)

    def Is_Valid(self, start: datetime, end: datetime, using_resources) -> bool:
        return True

    # Añadir eventos
    def add_events(self, event: Event):
        if self.Is_Valid(event.start, event.end, event.resources):

            for name, r in event.resources.items():
                self.resources[name].amount -= r.amount

            if self.events.get(event.name):
                print("This event already exist")
                inpt = input("Do you want to reewrite it, yes/no: ")
                if inpt == "yes":
                    self.events[event.name] = event
            else:
                self.events[event.name] = event

        else:
            print("That's not a valid event")
            

        # Remover eventos
    
    # Remover eventos
    def Remove_Events(self, event_name):
        if self.events.get(event_name):
            inpt = input("Do you want to remove this event, yes/no: ")
            if inpt == "yes":
                used_resourcers = self.events[event_name].resources

                for resource,r in used_resourcers.items():
                    self.resources[resource].amount += r.amount

                del self.events[event_name]
    
    # Ver detalles           
    def See_details(self, event_name):
        if self.events.get(event_name):
            print(f"Name of the event : {event_name}")
            print(f"Date of the event : start: {self.events[event_name].start} \r\n                    end: {self.events[event_name].end}")
            
            print("Resources details: ") 
            for r in self.events[event_name].resources.values():
                print(f"  {r.name}  =>  {r.amount}")
                
        else:
            print("That Event dosen't exist")

    # Obtener listado organizado
    def get_event_list(self) -> list:
        result = []
        for key, ev in self.events.items():
            resources = [{"name": rn, "amount": r.amount} for rn, r in ev.resources.items()]
            result.append({"key": key, 
                           "name": ev.name, 
                           "start": ev.start, 
                           "end": ev.end, 
                           "resources": resources})
            
        self.sort_by_date(result)
        return result
    
    # Metodo para hacer una tabla bonita para la consola
    def events_table(self) -> str:
        rows = []
        for ev in self.get_event_list():
            res_lines = [f"{r['name']} ({r['amount']})" for r in ev["resources"]]
            res_cell = "\n".join(res_lines) if res_lines else "-"
            rows.append([ev["name"], ev["start"].isoformat(), ev["end"].isoformat(), res_cell])

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
                parts = [ (cl[i] if i < len(cl) else "").ljust(w)
                        for cl, w in zip(cell_lines, widths) ]
                lines.append(" | ".join(parts))
            lines.append("-+-".join("-" * w for w in widths))
        return "\n".join(lines)

    # Metodo de ordenacion por datetime
    def sort_by_date(self, lst: list[dict[str,]]):
        lst.sort(key=lambda e: e["start"])

    # Obtener disponibilidad
    def find_next_slot_step(self, 
                            duration: timedelta, 
                            from_dt: datetime | None = None,
                            max_search: timedelta = timedelta(days=30),
                            resources_needed: dict[str, Resource] = None):
        
        step: timedelta = timedelta(minutes=30)
        
        if from_dt is None:
            from_dt = datetime.now()
        
        open_time = time(7,0)
        close_time = time(22,0)
        end_limit = from_dt + max_search
        next_start = from_dt
        
        
        while next_start + duration <= end_limit:
            candidate_end = next_start + duration
            
        if self.is_valid(next_start, candidate_end, resources_needed or {}):
            if next_start.hour >= open_time:
                if candidate_end.hour <= close_time:
                    return next_start, candidate_end
        next_start += step
        
        return None


# import uuid
# uuid.uuid4()

raw_resources = {
    # Espacios
    "Cancha de Football": 1,
    "Cancha de Tenis": 1,
    "Cancha de Basket (techada)": 1,
    "Cancha de Basket (aire libre)": 2,
    "Cancha de FootSal": 1,
    "Cancha de Boleyball": 1,
    "Cancha de Badmintong": 1,
    "Cancha de Cancha": 1,
    "Piscina Olimpica": 1,
    "Habitacion para juegos de mesa": 1,
    "Habitacion con Colchon": 1,
    "Pista de Carreras": 1,
    "Biosaludable (techado)": 1,
    "Biosaludable (aire libre)": 1,
    "Estadio de BaseBall": 1,
    "Pelota de Football": 15,
    "Pelota de Footsall": 15,
    "Pelota de Tenis": 50,
    "Pelota de Tenis de Mesa": 50,
    "Pelota de Boleyball": 15,
    "Pelota de Basket": 15,
    "Pelota de Cancha": 15,
    "Pelota de Badmintong": 15,
    "Pelota de Baseball": 30,
    "Raquetas de Cancha": 6,
    "Raquetas de Badmintong": 6,
    "Raquetas de Tenis": 6,
    "Raquetas de Tenis de Mesa": 6,
    "Bates de BaseBall": 30,
    "Guantes de BaseBall": 30,
    "Protectores de BaseBall": 30,
    "Cascos de BaseBall": 30,
    "Protectores de Karate": 30,
    "Cascos de Karate": 30,
    "Protectores de Taekwando": 30,
    "Cascos de Taekwando": 30,
    "Ned de Boleyball": 4,
    "Ned de Tenis": 4,
    "Ned de Tenis de Mesa": 4,
    "Porterias (Football)": 6,
    "Porterias (Footsall)": 6,
    "Arbitros": 5,
    "Personal de primeros auxilios": 5,
    "Boyas": 16,
    "Salva Vidas": 16,
    "Altavoces": 16,
    "Ambulacia": 2,
    "Microfonos": 8,
    "Sacos de Boxeo": 4,
    "Trampolin": 3,
    "Estrado de Premiaciones": 4,
}

# Convertir a instancias de Resource
global_resources = {
    name: Resource(name, amount) for name, amount in raw_resources.items()
}

raw_actual_resource = [
    ("Cancha de Football", 1),
    ("Pelota de Football", 3),
    ("Porterias (Football)", 2),
    ("Arbitros", 1),
    ("Personal de primeros auxilios", 2),
]

actual_resources = {
    name: Resource(name, amount) for name, amount in raw_actual_resource
}

e = Event(
    "Partido de Football",
    datetime(2025, 5, 7, 10, 0),
    datetime(2025, 5, 8, 12, 0),
    actual_resources,
)
b = Event(
    "Partido de Footbal",
    datetime(2025, 5, 7, 13, 0),
    datetime(2025, 5, 8, 14, 0),
    actual_resources,
)
c = Event(
    "Partido de Footba",
    datetime(2025, 5, 7, 15, 0),
    datetime(2025, 5, 8, 16, 0),
    actual_resources,
)
d = Event(
    "Partido de Foot",
    datetime(2025, 5, 7, 17, 0),
    datetime(2025, 5, 8, 18, 0),
    actual_resources,
)

p = Planner(global_resources, {})

p.add_events(b)
p.add_events(e)
p.add_events(d)
p.add_events(c)

print(p.events_table())




