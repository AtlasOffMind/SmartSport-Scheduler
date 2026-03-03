import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import calendar
from .utils_gui import Utils_Gui


class MultiInputDialog(tk.Toplevel):
    """Diálogo para introducir fecha y hora (año, mes, día, hora, minuto)"""

    def __init__(self, parent, title: str):
        super().__init__(parent)

        self.result = None
        self.title(title)

        self.withdraw()
        self.geometry("350x250")
        Utils_Gui.center_window(self)
        self.deiconify()

        self.resizable(True, True)

        # Obtener valores actuales
        now = datetime.now()

        tk.Label(self, text="year").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(self, text="month").grid(row=2, column=0, padx=10, pady=5)
        tk.Label(self, text="day").grid(row=4, column=0, padx=10, pady=5)
        tk.Label(self, text="hour").grid(row=0, column=1, padx=10, pady=5)
        tk.Label(self, text="min").grid(row=2, column=1, padx=10, pady=5)
        
        if title == "Event Start":
            tk.Label(self, text="(Open at 7am)").grid(row=1, column=2, padx=0, pady=5)
        if title == "Event End":
            tk.Label(self, text="(Close at 22pm)").grid(row=1, column=2, padx=0, pady=5)
            

        # Spinbox para año
        self.year_entry = tk.Spinbox(
            self, from_=1900, to=2100, width=10, wrap=False, command=self._update_day_range,
        )

        # Spinbox para mes
        self.month_entry = tk.Spinbox(
            self, from_=1, to=12, width=10, wrap=True, command=self._update_day_range
        )

        # Spinbox para día (rango ajustable)
        max_days = calendar.monthrange(now.year, now.month)[1]
        self.day_entry = tk.Spinbox(self, from_=1, to=max_days, width=10, wrap=True)

        # Spinbox para hora
        self.hour_entry = tk.Spinbox(self, from_=0, to=23, width=10, wrap=True)

        # Spinbox para minuto
        self.min_entry = tk.Spinbox(self, from_=0, to=59, width=10, wrap=True)

        self.year_entry.grid(row=1, column=0, padx=10)
        self.month_entry.grid(row=3, column=0, padx=10)
        self.day_entry.grid(row=5, column=0, padx=10)
        self.hour_entry.grid(row=1, column=1, padx=10)
        self.min_entry.grid(row=3, column=1, padx=10)

        tk.Button(self, text="Aceptar", command=self._on_ok).grid(
            row=7, column=1, columnspan=2, pady=15
        )
        
        

        # comportamiento modal
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _update_day_range(self):
        """Actualiza el rango de días válidos cuando cambia mes o año"""
        try:
            year = int(self.year_entry.get())
            month = int(self.month_entry.get())
            max_days = calendar.monthrange(year, month)[1]

            # Actualizar el spinbox de días
            self.day_entry.config(to=max_days)

            # Si el día actual es mayor que los días del nuevo mes, ajustarlo
            current_day = int(self.day_entry.get())
            if current_day > max_days:
                self.day_entry.set(max_days)
        except ValueError:
            pass

    def _on_ok(self):
        errors = []
        try:
            year = int(self.year_entry.get())
        except ValueError as ve:
            errors.append(ve)
        try: 
            month = int(self.month_entry.get())
        except ValueError as ve:
            errors.append(ve)
        try:
            day = int(self.day_entry.get())
        except ValueError as ve:
            errors.append(ve)
        try:
            hour = int(self.hour_entry.get())
        except ValueError as ve:
            errors.append(ve)
        try:
            min_val = int(self.min_entry.get())
        except ValueError as ve:
            errors.append(ve)
        try:
            dtime = datetime(year, month, day, hour, min_val)
        except Exception as ve:
            errors.append(ve)
            err_message = Utils_Gui._show_errors_dialog(errors)
            messagebox.showerror("Errores de validación", err_message)
            return

        self.result = dtime
        self.destroy()


