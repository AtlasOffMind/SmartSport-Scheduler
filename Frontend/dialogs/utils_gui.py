import tkinter as tk
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Utils_Gui:
    """Utilidades para la interfaz gráfica"""

    @staticmethod
    def center_window(window):
        """Centra una ventana en la pantalla"""
        window.update_idletasks()

        w = window.winfo_width()
        h = window.winfo_height()

        screen_w = window.winfo_screenwidth()
        screen_h = window.winfo_screenheight()

        x = (screen_w - w) // 2
        y = (screen_h - h) // 2

        window.geometry(f"{w}x{h}+{x}+{y}")
        
    @staticmethod
    def _show_errors_dialog(errors: list) -> str:
        """Muestra una ventana con todos los errores acumulados"""
        error_message = "\n".join([f"• {error}" for error in errors])
        return error_message
    
    @staticmethod
    def is_date_valid(start,end):
        day_start: datetime = datetime(start.year, start.month, start.day, 7, 0)
        day_end: datetime = datetime(start.year, start.month, start.day, 22, 0)

        if not isinstance(start, datetime) or not isinstance(end, datetime) or start >= end or start < day_start or end > day_end:
            return False
        return True
        