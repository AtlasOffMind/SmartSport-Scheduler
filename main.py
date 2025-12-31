#!/usr/bin/env python3
"""
SmartSport Scheduler - Aplicación principal
Gestor inteligente de planificación de eventos deportivos
"""

import sys
from pathlib import Path
import tkinter as tk

# Agregar raíz del proyecto al path para que los imports relativos funcionen
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Ahora importamos los módulos
from Frontend import PlannerGUI

def main():
    """Punto de entrada de la aplicación"""
    root = tk.Tk()
    app = PlannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
