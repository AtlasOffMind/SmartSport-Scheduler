import tkinter as tk
from tkinter import messagebox
from .utils_gui import Utils_Gui


class MultiInputDialog(tk.Toplevel):
    """Diálogo para introducir fecha y hora (año, mes, día, hora, minuto)"""

    def __init__(self, parent, title: str):
        super().__init__(parent)

        self.accepted = False
        self.result = None
        self.title(title)

        self.withdraw()
        self.geometry("300x200")
        Utils_Gui.center_window(self)
        self.deiconify()

        self.resizable(False, False)

        tk.Label(self, text="year").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(self, text="month").grid(row=2, column=0, padx=10, pady=5)
        tk.Label(self, text="day").grid(row=4, column=0, padx=10, pady=5)
        tk.Label(self, text="hour").grid(row=0, column=1, padx=10, pady=5)
        tk.Label(self, text="min").grid(row=2, column=1, padx=10, pady=5)

        self.year_entry = tk.Entry(self)
        self.month_entry = tk.Entry(self)
        self.day_entry = tk.Entry(self)
        self.hour_entry = tk.Entry(self)
        self.min_entry = tk.Entry(self)

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

    def _on_ok(self):
        try:
            year = int(self.year_entry.get())
            month = int(self.month_entry.get())
            day = int(self.day_entry.get())
            hour = int(self.hour_entry.get())
        except ValueError as v:
            messagebox.showerror("Invalid date", "Invalid date")
            return
        try:
            min = int(self.min_entry.get())
        except ValueError:
            min = 0

        self.result = (year, month, day, hour, min)
        self.accepted = True
        self.destroy()
