import tkinter as tk
from .utils_gui import Utils_Gui


class RequiredResourcesDialog(tk.Toplevel):
    """Ventana que muestra recursos obligatorios (co-requisites)"""

    def __init__(
        self,
        parent,
        selected_resources: dict[str, int],
        requires_dict: dict[str, list[str]],
        resource_name,
    ):
        super().__init__(parent)

        self.withdraw()
        self.title("Recursos Obligatorios")
        self.geometry("500x300")
        Utils_Gui.center_window(self)
        self.deiconify()

        self.accepted = False  # Flag para verificar si fue aceptada
        self.result_resources: dict[str, int] = selected_resources

        # Obtener recursos obligatorios para este recurso
        self.required_list = requires_dict.get(resource_name, [])

        # Mensaje informativo
        msg = f"Como ha usado el recurso '{resource_name}' necesita incluir los recursos obligatorios que van con este:"
        tk.Label(
            self, text=msg, font=("Arial", 10), wraplength=450, justify="left"
        ).pack(padx=15, pady=15)

        # Listbox con recursos obligatorios
        frame = tk.Frame(self)
        frame.pack(padx=15, pady=10, fill="both", expand=True)

        tk.Label(
            frame, text="Recursos que se agregarán:", font=("Arial", 9, "bold")
        ).pack(anchor="w")

        listbox = tk.Listbox(frame, height=8)
        listbox.pack(fill="both", expand=True, pady=5)

        for req_resource in self.required_list:
            selected_r_names = selected_resources.keys()
            if req_resource not in selected_r_names:
                listbox.insert(tk.END, f"• {req_resource}")

        # Botón OK (ahora con lambda para ejecutar al hacer click)
        tk.Button(self, text="Aceptar", command=self._on_accept).pack(pady=10)

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _on_accept(self):
        # Agregar recursos obligatorios a la lista
        for req_resource in self.required_list:
            self.result_resources[req_resource] = self.result_resources.get(
                req_resource, 0
            )

        self.accepted = True  # Marcar como aceptada
        self.destroy()
