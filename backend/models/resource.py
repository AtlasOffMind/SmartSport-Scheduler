from dataclasses import dataclass


@dataclass
class Resource:
    """Representa un recurso disponible en el centro deportivo"""
    name: str
    amount: int
