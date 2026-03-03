import tkinter as tk
from tkinter import messagebox
from backend import Resource
from .utils_gui import Utils_Gui
from .required_resources_dialog import RequiredResourcesDialog
from .cuantity_selected_resources import CuantitySelectedResources


class ResourceSelectorDialog(tk.Toplevel):
    """Diálogo para seleccionar recursos de forma interactiva"""

    global_resources: dict[str, Resource] = {}
    global_requires: dict[str, list[str]] = {}

    def __init__(self, parent, resources, planner_requires):
        super().__init__(parent)

        self.global_resources = resources
        self.global_requires = planner_requires

        self.withdraw()
        self.title("Seleccionar recursos")
        self.geometry("400x500")
        Utils_Gui.center_window(self)
        self.deiconify()

        self.result: dict[str, int] = {}

        # --- Listbox de recursos ---
        tk.Label(self, text="Recursos disponibles").pack(pady=(10, 0))

        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, height=20)

        self.listbox.pack(fill="x", padx=10)

        self.refresh_list()

        # --- Cantidad ---
        qty_frame = tk.Frame(self)
        qty_frame.pack(pady=10)

        # --- Botón agregar ---
        tk.Button(self, text="Agregar recurso(s)", command=self._add_resources).pack(
            pady=5
        )

        # --- Label de seleccionados ---
        self.selected_label = tk.Label(self, text="Seleccionados: ninguno")
        self.selected_label.pack(pady=5)

        # --- Botón aceptar ---
        tk.Button(self, text="Aceptar", command=self._on_accept).pack(pady=10)

        # Modal
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _add_resources(self):
        selection = self.listbox.curselection()

        if not selection:
            messagebox.showwarning("Recursos", "Seleccione al menos un recurso")
            return

        dict_temp = {}
        for idx in selection:
            name = self.listbox.get(idx)
            dict_temp[name] = dict_temp.get(name, 0)

        self.result = dict_temp.copy()
        self._update_label()

    def _update_label(self):
        texto = str(len(self.result.keys()))
        self.selected_label.config(text=f"Seleccionados: ({texto})")

    def _all_required_resources_present(self, resource_name, result_copy):
        """Verifica si todos los recursos requeridos para resource_name ya están en self.result"""
        required_list = self.global_requires.get(resource_name, [])

        # Si no hay recursos requeridos, retornar True (no hay nada que verificar)
        if not required_list:
            return True

        # Verificar si todos los recursos requeridos ya están en self.result
        for req_resource in required_list:
            if req_resource not in result_copy:
                return False  # Falta al menos un recurso requerido

        return True  # Todos los recursos requeridos ya están agregados

    def _on_accept(self):
        r_result = self.result.copy()
        for name in self.result.keys():
            if self.global_requires.get(name):
                # Verificar si los recursos requeridos ya están agregados
                if not self._all_required_resources_present(name, r_result):
                    dialog = RequiredResourcesDialog(
                        self, r_result, self.global_requires, name
                    )
                    # Si el usuario canceló la ventana de recursos obligatorios, volver a mostrar ResourceSelectorDialog
                    if not dialog.accepted:
                        return
                    r_result = dialog.result_resources

        self.result.update(r_result)
        # Verificar si todos los recursos tienen amount == 1
        all_single_amount = all(
            self.global_resources[name].amount == 1 for name in self.result.keys()
        )

        if all_single_amount:
            # Procesar directamente sin mostrar ventana de cantidades
            result_resources = {}
            for resource_name in self.result.keys():
                result_resources[resource_name] = Resource(resource_name, 1)
            self.result = result_resources

        else:
            # Mostrar ventana para seleccionar cantidades
            quantity_dialog = CuantitySelectedResources(
                self, self.result, self.global_resources
            )
            # Si el usuario canceló la ventana de cantidades, volver a mostrar ResourceSelectorDialog
            if not quantity_dialog.accepted:
                return
            self.result = quantity_dialog.result_resources
        self.destroy()

    def refresh_list(self):
        lst = list(self.global_resources.values())
        for r in lst:
            if r.amount > 0:
                self.listbox.insert(tk.END, r.name)
