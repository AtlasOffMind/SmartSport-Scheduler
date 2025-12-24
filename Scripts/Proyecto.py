from dataclasses import dataclass, field, asdict
from datetime import datetime
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


@dataclass
class Planner:
    # Estos son los recursos globales
    resources: dict[str, Resource] = field(default_factory=dict)
    events: dict[str, Event] = field(default_factory=dict)

    def Is_Valid(self, start: datetime, end: datetime, using_resources) -> bool:
        # Placeholder: aquí irá la comprobación real de solapamientos
        # y disponibilidad. Por ahora devuelve True para permitir pruebas.
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
    
    def Remove_Events(self, event_name):
        if self.events.get(event_name):
            inpt = input("Do you want to remove this event, yes/no: ")
            if inpt == "yes":
                used_resourcers = self.events[event_name].resources

                for resource,r in used_resourcers.items():
                    self.resources[resource].amount += r.amount

                del self.events[event_name]
                
    def See_details(self, event_name):
        if self.events.get(event_name):
            print(f"Name of the event : {event_name}")
            print(f"Date of the event : start: {self.events[event_name].start}, end: {self.events[event_name].end}")
            
            print("Resources details: ") 
            for r in self.events[event_name].resources.values():
                print(f"  {r.name}  =>  {r.amount}")

    # def Get_Event_List():
    #     sorted_events = sort_by_date()
    #     return sorted_events


    # #TODO crear el metodo este de revision

    # def sort_by_date():
    #     date_lst = []
    #     value_lst = []
    #     keys_lst = [*events]
    #     for i,value in enumerate([*events.values()]):
    #         date,lst = value
    #         date_lst.append((date, i))
    #         value_lst.append(lst)

    # #TODO aun no he creado el criterio para ordenar por fechas
    #     date_lst.sort()

    #     temp={}
    #     for tple in date_lst:
    #         date, i = tple
    #         (k,d,r)= keys_lst[i], date, value_lst[i]
    #         temp[k] = (d,r)

    #     return temp

  


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
    datetime(2025, 5, 7, 12, 0),
    actual_resources,
)

p = Planner(global_resources, {})

p.add_events(e)

p.See_details("Partido de Football")

print(p.events)


