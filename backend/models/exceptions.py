from dataclasses import dataclass


@dataclass
class DecisionRequired(Exception):
    """Excepción que requiere decisión del usuario"""
    message: str = ""

    def __str__(self):
        return self.message
