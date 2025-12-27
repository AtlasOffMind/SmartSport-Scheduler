import sys
import unittest
from pathlib import Path

# ensure Scripts is importable
ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "Scripts"
sys.path.insert(0, str(SCRIPTS))

from Proyecto import (
    Planner,
    Event,
    Resource,
    save_planner,
    load_planner,
    get_default_data_path,
)
from datetime import datetime, timedelta
import shutil


class PlannerTests(unittest.TestCase):
    def test_save_and_load_roundtrip(self):
        # Use the module-level planner if available, otherwise create a minimal one
        p = Planner({"Cancha de Tenis": Resource("Cancha de Tenis", 1)})
        path = get_default_data_path()
        # make sure we start clean
        try:
            if path.exists():
                path.unlink()
        except Exception:
            pass

        save_planner(p, None)
        self.assertTrue(path.exists())

        loaded = load_planner(None)
        self.assertIsInstance(loaded, Planner)
        self.assertIn("Cancha de Tenis", loaded._resources)

    def test_is_valid_detects_conflict(self):
        # single unit resource
        pl = Planner({"Cancha de Tenis": Resource("Cancha de Tenis", 1)})
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(hours=1)
        using = {"Cancha de Tenis": Resource("Cancha de Tenis", 1)}

        # no events yet -> valid
        self.assertTrue(pl.is_valid(start, end, using))

        # add an overlapping event that consumes the same resource
        ev = Event("Existing", start, end, using)
        pl.events["Existing"] = ev

        # now same request should be invalid (1 used + 1 requested > 1 available)
        self.assertFalse(pl.is_valid(start, end, using))

    def test_requires_enforced(self):
        # Pelota de Tenis requires Cancha de Tenis and Raquetas de Tenis (per defaults)
        pl = Planner(
            {
                "Pelota de Tenis": Resource("Pelota de Tenis", 2),
                "Cancha de Tenis": Resource("Cancha de Tenis", 1),
            }
        )
        start = datetime.now() + timedelta(days=2)
        end = start + timedelta(hours=1)

        # request only the ball -> should be invalid because requires includes Raquetas de Tenis
        using = {"Pelota de Tenis": Resource("Pelota de Tenis", 1)}
        self.assertFalse(pl.is_valid(start, end, using))


if __name__ == "__main__":
    unittest.main()
