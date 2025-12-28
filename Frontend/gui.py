import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import calendar
import tkinter as tk
from tkinter import messagebox, simpledialog

# make Scripts importable
ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "Scripts"
sys.path.insert(0, str(SCRIPTS))

from Proyecto import load_planner, save_planner, Resource, Event


class PlannerGUI:
    def __init__(self, root: tk):
        self.root = root
        root.title("SmartSport Scheduler")
        root.minsize(600, 300)

        # load planner
        try:
            self.planner = load_planner(None)
        except Exception:
            # fallback: create empty planner via Proyecto (load_planner constructs Planner)
            self.planner = load_planner(None)

        # Events list (main area). Make it expand with the window.
        self.events_listbox = tk.Listbox(root, font= 8,width=80, height=15)
        self.events_listbox.grid(
            row=0,  column=0, columnspan=3, padx=8, pady=30, sticky="nsew"
        )

        self.events_label = tk.Label(
            root,
            text="Eventos existentes",
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
        tk.Button(root, text="Find Next Slot", font= 10, command=self.find_slot).grid(
            row=2, column=1, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="View Details", font= 10, command=self.view_selected).grid(
            row=2, column=2, sticky="we", padx=4, pady=4
        )

        self.refresh()

    # region Bottons
    def refresh(self):
        self.events_listbox.delete(0, tk.END)
        
        for name, ev in sorted(self.planner.events.items(), key=lambda t: t[1].start):
            self.events_listbox.insert(tk.END,name)

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

    def add_event_dialog(self):
        name = simpledialog.askstring("Event name", "Name:")
        if not name:
            return
        start_s = simpledialog.askstring(
            "Start", "Start datetime (ISO or YYYY-MM-DD HH:MM):"
        )
        if not start_s:
            return
        end_s = simpledialog.askstring("End", "End datetime (ISO or YYYY-MM-DD HH:MM):")
        if not end_s:
            return
        resources_s = simpledialog.askstring(
            "Resources",
            "Resources (comma separated name:amount), e.g. 'Cancha de Tenis:1, Pelota de Tenis:3':",
        )
        try:
            start = self.parse_datetime(start_s)
            end = self.parse_datetime(end_s)
        except Exception as ex:
            messagebox.showerror("Invalid date", str(ex))
            return

        resources = {}
        if resources_s:
            try:
                parts = [p.strip() for p in resources_s.split(",") if p.strip()]
                for p in parts:
                    if ":" in p:
                        rn, amt = p.split(":", 1)
                        rn = rn.strip()
                        amt = int(amt.strip())
                        resources[rn] = Resource(rn, amt)
                    else:
                        messagebox.showerror("Invalid resource format", p)
                        return
            except Exception as ex:
                messagebox.showerror("Invalid resources", str(ex))
                return

        # validate using planner.is_valid
        try:
            ok = self.planner.is_valid(start, end, resources)
        except Exception as ex:
            messagebox.showerror("Validation error", str(ex))
            return

        if not ok:
            messagebox.showwarning(
                "Not valid",
                "The event or resources are not valid or conflict with existing events.",
            )
            return

        # apply: deduct resources and add event
        for rn, r in resources.items():
            if rn not in self.planner._resources:
                messagebox.showerror("Unknown resource", rn)
                return
            self.planner._resources[rn].amount -= r.amount

        ev = Event(name, start, end, resources)
        self.planner.events[name] = ev
        self.refresh()

    def delete_selected(self):
        sel = self.events_listbox.curselection()
        if not sel:
            messagebox.showinfo("Details", "No event selected")
            return
        idx = sel[0]
        name = self.events_listbox.get(idx)
        if messagebox.askyesno("Delete", f"Delete event '{name}'?"):
            ev = self.planner.events.get(name)
            if ev:
                for rn, r in ev.resources.items():
                    if rn in self.planner._resources:
                        self.planner._resources[rn].amount += r.amount
                del self.planner.events[name]
                self.refresh()

    def save(self):
        try:
            save_planner(self.planner, None)
            messagebox.showinfo("Saved", "Planner saved to disk")
        except Exception as ex:
            messagebox.showerror("Save error", str(ex))

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

    def view_selected(self):
        sel = self.events_listbox.curselection()
        if not sel:
            messagebox.showinfo("Details", "No event selected")
            return
        name = self.events_listbox.get(sel[0])
        ev = self.planner.events.get(name)
        if not ev:
            messagebox.showerror("Details", "Event not found")
            return
        s = ev.start.strftime("%Y-%m-%d %H:%M")
        e = ev.end.strftime("%Y-%m-%d %H:%M")
        resources = (
            "\n     ".join(f"{n}: {r.amount}" for n, r in ev.resources.items()) or "-"
        )

        spaced_r = f"\n" + "    " + f"{resources}"

        messagebox.showinfo(
            "Event details",
            f"Name: {ev.name}\nStart: {s}\nEnd: {e}\nResources:\n     {resources}",
        )

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

    def _on_day_click(self, dt: date):
        self.selected_date = dt
        for d, b in self.day_buttons.items():
            b.configure(relief="raised")
        if dt in self.day_buttons:
            self.day_buttons[dt].configure(relief="sunken")

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
