import tkinter as tk
from tkinter import messagebox
from backend import Resource
from .utils_gui import Utils_Gui


class CuantitySelectedResources(tk.Toplevel):
    """Diálogo para seleccionar cantidades de recursos"""

    def __init__(
        self,
        parent,
        resources_selected: dict[str, int],
        original_dict: dict[str, Resource],
    ):
        super().__init__(parent)

        self.withdraw()
        self.title("Seleccionar cantidad de recursos")
        self.accepted = False  # Flag para verificar si fue aceptada
        self.result_resources: dict[str, Resource] = {}
        self.spinbox_dict: dict[str, tk.Spinbox] = {}

        # Header con títulos
        header_frame = tk.Frame(self)
        header_frame.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        tk.Label(header_frame, text="Recurso", font=("Arial", 10, "bold")).pack(
            side="left", expand=True
        )
        tk.Label(
            header_frame, text="Cantidad disponible", font=("Arial", 10, "bold")).pack(
            side="left", padx=20
        )
        tk.Label(header_frame, text="Cantidad a usar", font=("Arial", 10, "bold")).pack(
            side="left", padx=20
        )

        r = 1

        # Crear Spinbox para cada recurso seleccionado
        for resource_name in resources_selected.keys():
            if original_dict[resource_name].amount > 1:
                resource = original_dict[resource_name]
                max_amount = resource.amount

                # Label del recurso
                tk.Label(self, text=resource_name).grid(
                    row=r, column=0, padx=10, pady=8, sticky="w"
                )

                # Label cantidad disponible
                tk.Label(self, text=str(max_amount)).grid(
                    row=r, column=0, padx=200, pady=8
                )

                # Spinbox para cantidad a usar
                spinbox = tk.Spinbox(self, from_=1, to=max_amount, width=5)
                spinbox.grid(row=r, column=1, padx=10, pady=8)
                self.spinbox_dict[resource_name] = spinbox

                r += 1
            else:
                self.spinbox_dict[resource_name] = 1

        # Botón Aceptar
        tk.Button(
            self, text="Aceptar", command=self._on_accept, bg="#4CAF50", fg="white"
        ).grid(row=r, column=0, columnspan=2, pady=20)

        # Ajustar tamaño de ventana según contenido
        self.update_idletasks()
        width = self.winfo_reqwidth() + 20
        height = self.winfo_reqheight() + 20
        self.geometry(f"{width}x{height}")
        Utils_Gui.center_window(self)
        self.deiconify()

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _on_accept(self):
        for resource_name, spinbox in self.spinbox_dict.items():
            if isinstance(spinbox, tk.Spinbox):
                try:
                    amount = int(spinbox.get())
                    if amount > 0:
                        self.result_resources[resource_name] = Resource(
                            resource_name, amount
                        )
                except ValueError:
                    messagebox.showerror(
                        "Error", f"Cantidad inválida para {resource_name}"
                    )
                    return

            else:
                amount = spinbox
                self.result_resources[resource_name] = Resource(resource_name, amount)
        self.accepted = True  # Marcar como aceptada
        self.destroy()
