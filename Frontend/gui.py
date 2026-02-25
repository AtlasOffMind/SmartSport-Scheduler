import sys
from pathlib import Path
from datetime import datetime, date
import calendar
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

# make backend importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend import (
    load_planner,
    save_planner,
    create_planner,
    Event,
    DecisionRequired,
)

from .dialogs import MultiInputDialog, ResourceSelectorDialog


class PlannerGUI:
    def __init__(self, root: tk):
        self.root = root
        root.title("SmartSport Scheduler")
        root.minsize(800, 400)

        # load planner
        self.planner = create_planner()

        # Configure grid weights so widgets grow when window is resized
        for i in range(8):
            root.columnconfigure(i, weight=1)
        root.rowconfigure(1, weight=1)

        # ===== TOOLBAR (Row 0) =====
        toolbar = tk.Frame(root, relief="raised", bd=1)
        toolbar.grid(row=0, column=0, columnspan=8, sticky="ew", padx=0, pady=0)

        buttons = [
            ("Refresh", self.refresh),
            ("Add Event", self.add_event_dialog),
            ("Delete Event", self.delete_selected),
            ("Save", self.save),
            ("Load Planner", self.load_planner),
            ("Find Next Slot", self.find_slot),
            ("View Details", self.view_selected),
        ]

        for idx, (text, command) in enumerate(buttons):
            btn = tk.Button(toolbar, text=text, command=command, font=8, padx=5, pady=3)
            btn.pack(side="left", padx=2, pady=4)
            toolbar.columnconfigure(idx, weight=1)

        # ===== CONTENT AREA (Row 1) =====
        # Title of the listboxes
        self.events_label = tk.Label(root, text="Global events", font=(12))
        self.events_label.grid(row=1, column=0, columnspan=7, pady=(6, 0), sticky="n")

        # Events list (main area). Make it expand with the window.
        self.events_listbox = tk.Listbox(root, font=8, width=80, height=15)
        self.events_listbox.grid(
            row=1, column=0, columnspan=7, padx=8, pady=8, sticky="nsew"
        )

        # Calendar area on the right
        self.calendar_frame = tk.Frame(root, bd=1, relief="sunken")
        self.calendar_frame.grid(
            row=1, column=7, sticky="nsew", padx=8, pady=8
        )

        # calendar state
        today = date.today()
        self.cal_year = today.year
        self.cal_month = today.month
        self.selected_date = None
        self.day_buttons = {}
        self._build_calendar_widgets()
        self._render_calendar()

        self.refresh()
    # Aprobado x Chayanne
    def refresh(self):
        self.events_listbox.delete(0, tk.END)
        for dct in self.planner.get_event_list():
            self.events_listbox.insert(tk.END, dct["name"])
        self._render_calendar()

    # Aprobado x Chayanne
    def add_event_dialog(self):
        name = simpledialog.askstring("Event name", "Name:")
        if not name:
            return

        accepted_s = False
        date = MultiInputDialog(self.root, "Event Start")
        if not date.result:
            return
        s_y, s_m, s_d, s_h, s_min = date.result
        accepted_s = date.accepted

        accepted_e = False
        date = MultiInputDialog(self.root, "Event End")
        if not date.result:
            return
        e_y, e_m, e_d, e_h, e_min = date.result
        accepted_e = date.accepted

# TODO mostrar todos los errores
        try:
            start = datetime(s_y, s_m, s_d, s_h, s_min)
            end = datetime(e_y, e_m, e_d, e_h, e_min)
        except Exception as ex:
            messagebox.showerror("Invalid date", str(ex))
            return

        resources = {}

        accepted_r = False
        dialog = ResourceSelectorDialog(
            self.root, self.planner._resources, self.planner.requires
        )

        if dialog.result:
            resources = dialog.result
            accepted_r = dialog.accepted

        # validate using planner.is_valid
        if all((accepted_s, accepted_e, accepted_r)):
            event = Event(name, start, end, resources)
            try:
                self.planner.add_events(event)
            except ValueError as ex:
                messagebox.showerror("Exception: ", str(ex))
                return
            except DecisionRequired as d:
                decision = messagebox.askyesno(
                    "Needed confirmation", f"{str(d)} \n Do you want to reewrite it?"
                )
                if decision:
                    self.planner.force_add(event)

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
            save_planner(filename, self.planner, None)
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

        path = filedialog.askopenfile(
            title="Cargar planner",
            initialdir=Path.cwd(),  # carpeta del proyecto
            filetypes=[("Planner JSON", "*.json")],
        )
        # load planner
        try:
            self.planner = load_planner(path.name)
        except AttributeError as ex:
            pass
        except Exception as ex:
            messagebox.showerror(f"Error", str(ex))

        self.refresh()

    # enderegion

    # ------------------ Calendar helpers ------------------

    # TODO arreglar el calendario para q en la parte de abajo salgan las horas predeterminadas del dia y
    # q cuando toques un dia te salgan los eventos correspondientes en la hora q ocupan
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
                command=lambda dt=dt: self._on_day_click(dt),
            )

            if self._is_day_occupied(dt):
                btn.configure(bg="#ffcccc")
            elif dt == date.today() and not self._is_day_occupied(dt):
                btn.configure(bg="#656dff")
            else:
                btn.configure(bg="#ccffcc")

            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nnsew")

            self.day_buttons[dt] = btn

            col += 1
            if col > 6:
                col = 0
                row += 1

    # Aprobado x Chayanne
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
        evs = [
            ev
            for ev in self.planner.events.values()
            if ev.start.date() <= dt <= ev.end.date()
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

    # Aprobado x Chayanne
    def _prev_month(self):
        if self.cal_month == 1:
            self.cal_month = 12
            self.cal_year -= 1
        else:
            self.cal_month -= 1
        self._render_calendar()

    # Aprobado x Chayanne
    def _next_month(self):
        if self.cal_month == 12:
            self.cal_month = 1
            self.cal_year += 1
        else:
            self.cal_month += 1
        self._render_calendar()
