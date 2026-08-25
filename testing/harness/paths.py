"""Where the suite reads and writes: the repo, the settings file, the reports."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS_FILE = ROOT / "settings.env"
RESULTS_DIR = ROOT / "testing" / "results"
