import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import calendar
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from dataclasses import dataclass

# make Scripts importable
ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "Scripts"
sys.path.insert(0, str(SCRIPTS))

from Proyecto import load_planner, save_planner, Resource, Event, Utils, DecisionRequired

@dataclass
class Utils_Gui():
    def center_window(window):
        window.update_idletasks()

        w = window.winfo_width()
        h = window.winfo_height()

        screen_w = window.winfo_screenwidth()
        screen_h = window.winfo_screenheight()

        x = (screen_w - w) // 2
        y = (screen_h - h) // 2

        window.geometry(f"{w}x{h}+{x}+{y}")

class MultiInputDialog(tk.Toplevel):
    def __init__(self, parent, title: str):
        super().__init__(parent)

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
        try:
            min = int(self.min_entry.get())
        except ValueError:
            min = 0 


        self.result = (year,month,day,hour,min)
        self.destroy()

class CuantitySelectedResources(tk.Toplevel):
    def __init__(self, parent, resources_selected: dict[str,int], original_dict: dict[str,Resource]):
        super().__init__(parent)
        
        self.withdraw()
        self.title("Seleccionar cantidad de recursos")
        self.geometry("400x500")
        Utils_Gui.center_window(self)
        # self.resizable(False, False)
        self.deiconify()
        
        self.result_events: dict[str, Event] = {}
        
        r = 1
        label_list = []
        
        #TODO ya esta mierda funciona (pero falta)
            # hay q agregar boton de aceptar, guardar todas las cantidades,
            # hay q poner un label q diga en la row=0 nombre del recurso, actual amount 
            # hay q hacer otra clase para agregarle los recusos obligatorios 
            # hay q revisar las exclusiones
        for n in resources_selected.keys():
            if original_dict[n].amount > 1:
                label_list.append((tk.Label(self, text=n).grid(row=r,  column=0, columnspan=1, padx=1, pady=8, sticky="nsew"),
                 tk.Spinbox(self,from_=1,to=100,width=5).grid(row=r,  column=1, columnspan=1, padx=30, pady=8, sticky="nsew")))
                r += 1       
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
        
        
        
        

class ResourceSelectorDialog(tk.Toplevel):
    global_resources = {}
    
    def __init__(self, parent, resources):
        super().__init__(parent)
        
        self.global_resources = resources

        self.withdraw()
        self.title("Seleccionar recursos")
        self.geometry("400x500")
        Utils_Gui.center_window(self)
        # self.resizable(False, False)
        self.deiconify()

        self.result:dict[str,int] = {}

        # --- Listbox de recursos ---
        tk.Label(self, text="Recursos disponibles").pack(pady=(10, 0))

        self.listbox = tk.Listbox(self,selectmode=tk.MULTIPLE,height=20)
        
        self.listbox.pack(fill="x", padx=10)

        self.refresh_list()

        # --- Cantidad ---
        qty_frame = tk.Frame(self)
        qty_frame.pack(pady=10)

        # tk.Label(qty_frame, text="Cantidad:").pack(side="left")

        # self.qty_spin = tk.Spinbox(qty_frame,from_=1,to=100,width=5)
        # self.qty_spin.pack(side="left", padx=5)

        # --- Botón agregar ---
        tk.Button(self,text="Agregar recurso(s)",command=self._add_resources).pack(pady=5)

        # --- Label de seleccionados ---
        self.selected_label = tk.Label(self, text="Seleccionados: ninguno")
        self.selected_label.pack(pady=5)

        # --- Botón aceptar ---
        tk.Button(self,text="Aceptar",command=self._on_accept).pack(pady=10)

        # Modal
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _add_resources(self):
        selection = self.listbox.curselection()

        if not selection:
            messagebox.showwarning("Recursos","Seleccione al menos un recurso")
            return

        # qty = int(self.qty_spin.get())

        for idx in selection:
            name = self.listbox.get(idx)
            self.result[name] = self.result.get(name, 0) #+ qty

        self._update_label()
        
    def _update_label(self):
        texto =str(len(self.result.keys())) 
        self.selected_label.config( text=f"Seleccionados: ({texto})" )
    
    def _on_accept(self):
        self.destroy()
    
    def refresh_list(self):
        lst = list(self.global_resources.values())
        for r in lst:
            if r.amount > 0:
                self.listbox.insert(tk.END, r.name)
  
class PlannerGUI:
    def __init__(self, root: tk):
        self.root = root
        root.title("SmartSport Scheduler")
        root.minsize(600, 300)

        # load planner
        self.planner = Utils.create_planner()
        
        # Events list (main area). Make it expand with the window.
        self.events_listbox = tk.Listbox(root, font= 8,width=80, height=15)
        self.events_listbox.grid(
            row=0,  column=0, columnspan=3, padx=8, pady=30, sticky="nsew"
        )

        # Title of the listboxes
        self.events_label = tk.Label(
            root,
            text="Global events",
            font=(12)
        )
        self.events_label.grid(
            row=0,
            column=0,
            columnspan=3,
            pady=(6, 0),
            sticky="n"
        )

        # Configure grid weights so widgets grow when window is resized
        for i in range(4):
            root.columnconfigure(i, weight=1)
        root.rowconfigure(0, weight=1)

        # Calendar area on the right
        self.calendar_frame = tk.Frame(root, bd=1, relief="sunken")  
        self.calendar_frame.grid(
            row=0, column=3, rowspan=1, sticky="nsew", padx=8, pady=30
        )

        # calendar state
        today = date.today()
        self.cal_year = today.year
        self.cal_month = today.month
        self.selected_date = None
        self.day_buttons = {}
        self._build_calendar_widgets()
        self._render_calendar()

        # Buttons (use sticky so they expand horizontally)
        tk.Button(root, text="Refresh", font= 10, command=self.refresh).grid(
            row=1, column=0, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="Add Event", font= 10, command=self.add_event_dialog).grid(
            row=1, column=1, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="Delete Event", font= 10, command=self.delete_selected).grid(
            row=1, column=2, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="Save", font= 10, command=self.save).grid(
            row=1, column=3, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="Load Planner", font= 10, command=self.load_planner).grid(
            row=2, column=0, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="Find Next Slot", font= 10, command=self.find_slot).grid(
            row=2, column=1, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="View Details", font= 10, command=self.view_selected).grid(
            row=2, column=2, sticky="we", padx=4, pady=4
        )

        self.refresh()
   
    # Aprobado x Chayanne
    def refresh(self):
        self.events_listbox.delete(0, tk.END)
        for dct in self.planner.get_event_list():
                self.events_listbox.insert(tk.END, dct["name"])
        self._render_calendar()

    def parse_datetime(self, text: str):
        try:
            return datetime.fromisoformat(text)
        except Exception:
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"):
                try:
                    return datetime.strptime(text, fmt)
                except Exception:
                    continue
        raise ValueError("Invalid datetime format")

    #TODO corregir este metodo xq no llama al metodo del Planner. 
    #      Ademas agregarle todas las opciones necesarias para crear un nuevo evento legal 
    def add_event_dialog(self):
        # name = simpledialog.askstring("Event name", "Name:")
        # if not name:
        #     return
        
        # date = MultiInputDialog(root, "Event Start")
        # if not date.result:
        #     return
        # s_y,s_m,s_d,s_h,s_min = date.result
        
        # date = MultiInputDialog(root, "Event End")
        # if not date.result:
        #     return
        # e_y,e_m,e_d,e_h,e_min = date.result
        
        # try:
        #     start = datetime(s_y,s_m,s_d,s_h,s_min)
        #     end = datetime(e_y,e_m,e_d,e_h,e_min)
            
        #     # start = self.parse_datetime(start_s)
        #     # end = self.parse_datetime(end_s)
        # except Exception as ex:
        #     messagebox.showerror("Invalid date", str(ex))
        #     return

        resources = {}
        
        dialog = ResourceSelectorDialog(root, self.planner._resources)
        dialog = CuantitySelectedResources(root,dialog.result,self.planner._resources)
        if dialog.result:
            resources = dialog.result
            
            

        # validate using planner.is_valid
        try:
            self.planner.add_events(start, end, resources)
        except ValueError as ex:
            messagebox.showerror("Exception: ", str(ex))
            return
        except DecisionRequired as d:
                decision = messagebox.askyesno("Needed confirmation", 
                                               f"{str(d)} \n Do you want to reewrite it?" )
        
        self.refresh()
        
    # Aprobado x Chayanne
    def delete_selected(self):
        sel = self.events_listbox.curselection()
        if not sel:
            messagebox.showinfo("Details", "No event selected")
            return
        idx = sel[0]
        name = self.events_listbox.get(idx)
        
        if messagebox.askyesno("Delete", f"Delete event '{name}'?"):
           try:
            self.planner.remove_event(name)
            self.refresh()
            self._render_calendar()
           except Exception as e:
                messagebox.showerror("Error", str(e))

    # Aprobado x Chayanne
    def save(self):
        try:
            filename = simpledialog.askstring("File name", "")
            save_planner(filename,self.planner, None)
            messagebox.showinfo("Saved", "Planner saved to disk")
        except Exception as ex:
            messagebox.showerror("Save error", str(ex))

    # Creo q este metodo ya funciona
    def find_slot(self):
        res = self.planner.find_next_slot_step()
        if not res:
            messagebox.showinfo("Find slot", "No slot found in search window")
            return
        start, end = res
        messagebox.showinfo(
            "Next slot",
            f"{start.strftime('%Y-%m-%d %H:%M')} -> {end.strftime('%Y-%m-%d %H:%M')}",
        )

    # Aprobado x Chayanne
    def view_selected(self):
        sel = self.events_listbox.curselection()
        if not sel:
            messagebox.showinfo("Details", "No event selected")
            return
        name = self.events_listbox.get(sel[0])
        ev = self.planner.see_details(name)
        if not ev:
            messagebox.showerror("Details", "Event not found")
            return
        s = ev.start.strftime("%Y-%m-%d %H:%M")
        e = ev.end.strftime("%Y-%m-%d %H:%M")
        resources = (
            "\n     ".join(f"{n}: {r.amount}" for n, r in ev.resources.items()) or "-"
        )

        messagebox.showinfo(
            "Event details",
            f"Name: {ev.name}\nStart: {s}\nEnd: {e}\nResources:\n     {resources}",
        )

    # Aprobado x Chayanne
    def load_planner(self):
        
        path = filedialog.askopenfile(title="Cargar planner",
                                      initialdir=Path.cwd().parent,  # carpeta del proyecto
                                      filetypes=[("Planner JSON", "*.json")]
        )
        # load planner
        try:
            self.planner = load_planner(path.name)
        except Exception as ex:
            messagebox.showerror("Invalid path", str(ex))
            
        self.refresh()

    # enderegion

    # ------------------ Calendar helpers ------------------
    def _build_calendar_widgets(self):
        header = tk.Frame(self.calendar_frame)
        header.pack(fill="x", padx=4, pady=2)

        prev_btn = tk.Button(header, text="<", width=3, command=self._prev_month)
        prev_btn.pack(side="left")
        self.month_label = tk.Label(header, text="", width=20)
        self.month_label.pack(side="left", expand=True)
        next_btn = tk.Button(header, text=">", width=3, command=self._next_month)
        next_btn.pack(side="right")

        # weekday labels (use grid + columnconfigure so they expand with the window)
        days_frame = tk.Frame(self.calendar_frame)
        days_frame.pack(fill="x", padx=4)
        for i, wd in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            lbl = tk.Label(days_frame, text=wd)
            lbl.grid(row=0, column=i, sticky="we", padx=1)
            days_frame.columnconfigure(i, weight=1)

        # grid for days
        self.days_grid = tk.Frame(self.calendar_frame)
        self.days_grid.pack(fill="both", padx=4, pady=4)

    # Aprobado x Chayanne
    def _render_calendar(self):
        # clear previous buttons
        for child in self.days_grid.winfo_children():
            child.destroy()
        self.day_buttons.clear()

        self.month_label.config(
            text=f"{calendar.month_name[self.cal_month]} {self.cal_year}"
        )

        first_weekday, ndays = calendar.monthrange(self.cal_year, self.cal_month)
        row = 0
        col = first_weekday
        
        # permitir que el grid del calendario se expanda
        for i in range(7):
            self.days_grid.columnconfigure(i, weight=1) 
        for i in range(6):
            self.days_grid.rowconfigure(i, weight=1)     
        
        for d in range(1, ndays + 1):
            dt = date(self.cal_year, self.cal_month, d)
            btn = tk.Button(
                self.days_grid,
                text=str(d),
                font=(12),
                # width=4,
                # height=4,
                command=lambda dt=dt: self._on_day_click(dt),
            )
            if self._is_day_occupied(dt):
                btn.configure(bg="#ffcccc")
            else:
                btn.configure(bg="#ccffcc")
        
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nnsew")

            
            self.day_buttons[dt] = btn

            col += 1
            if col > 6:
                col = 0
                row += 1

    def _is_day_occupied(self, dt: date) -> bool:
        for ev in self.planner.events.values():
            ev_start_date = ev.start.date()
            ev_end_date = ev.end.date()
            if ev_start_date <= dt <= ev_end_date:
                return True
        return False

    # Aprobado x Chayanne
    def _on_day_click(self, dt: date):
        self.selected_date = dt
        for d, b in self.day_buttons.items():
            b.configure(relief="raised")
        if dt in self.day_buttons:
            self.day_buttons[dt].configure(relief="sunken")

        self.planner.sort_events()
        evs = [ev for ev in self.planner.events.values() if ev.start.date() <= dt <= ev.end.date()
        ]
        if not evs:
            messagebox.showinfo(
                "Events on {0}".format(dt.isoformat()), "No events on this day"
            )
            return
        lines = []
        for ev in evs:
            lines.append(
                f"{ev.name}: {ev.start.strftime('%H:%M')} - {ev.end.strftime('%H:%M')}"
            )
        messagebox.showinfo(f"Events on {dt.isoformat()}", "\n".join(lines))

    def _prev_month(self):
        if self.cal_month == 1:
            self.cal_month = 12
            self.cal_year -= 1
        else:
            self.cal_month -= 1
        self._render_calendar()

    def _next_month(self):
        if self.cal_month == 12:
            self.cal_month = 1
            self.cal_year += 1
        else:
            self.cal_month += 1
        self._render_calendar()


if __name__ == "__main__":
    root = tk.Tk()
    app = PlannerGUI(root)
    root.mainloop()
