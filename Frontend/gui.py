import sys
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

# make Scripts importable
ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "Scripts"
sys.path.insert(0, str(SCRIPTS))

from Proyecto import load_planner, save_planner, Resource, Event


class PlannerGUI:
    def __init__(self, root):
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
        self.events_listbox = tk.Listbox(root, width=80, height=15)
        self.events_listbox.grid(
            row=0, column=0, columnspan=4, padx=8, pady=8, sticky="nsew"
        )

        # Configure grid weights so widgets grow when window is resized
        for i in range(4):
            root.columnconfigure(i, weight=1)
        root.rowconfigure(0, weight=1)

        # Buttons (use sticky so they expand horizontally)
        tk.Button(root, text="Refresh", command=self.refresh).grid(
            row=1, column=0, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="Add Event", command=self.add_event_dialog).grid(
            row=1, column=1, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="Delete Event", command=self.delete_selected).grid(
            row=1, column=2, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="Save", command=self.save).grid(
            row=1, column=3, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="Find Next Slot", command=self.find_slot).grid(
            row=2, column=1, sticky="we", padx=4, pady=4
        )
        tk.Button(root, text="View Details", command=self.view_selected).grid(
            row=2, column=2, sticky="we", padx=4, pady=4
        )

        self.refresh()

    def refresh(self):
        self.events_listbox.delete(0, tk.END)
        for name, ev in sorted(self.planner.events.items(), key=lambda t: t[1].start):
            # show only the event name in the list; details available via 'View Details'
            self.events_listbox.insert(tk.END, name)

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
        messagebox.showinfo("Next slot", f"{start.strftime("%Y-%m-%d %H:%M")} -> {end.strftime("%Y-%m-%d %H:%M")}")

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


if __name__ == "__main__":
    root = tk.Tk()
    app = PlannerGUI(root)
    root.mainloop()
