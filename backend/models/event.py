from dataclasses import dataclass
from datetime import datetime
from .resource import Resource


@dataclass
class Event:
    """Representa un evento (actividad) que requiere recursos y horario"""

    name: str
    start: datetime
    end: datetime
    resources: dict[str, Resource]
