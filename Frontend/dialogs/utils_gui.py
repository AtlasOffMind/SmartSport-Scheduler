import tkinter as tk
from dataclasses import dataclass


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
