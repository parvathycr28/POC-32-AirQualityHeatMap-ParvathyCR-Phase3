from pathlib import Path
import runpy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRACK_SCRIPT = (
    PROJECT_ROOT
    / "data-science"
    / "scripts"
    / "track-specific"
    / "track_a_comparative_intelligence.py"
)

if not TRACK_SCRIPT.exists():
    raise FileNotFoundError(f"Track A script not found: {TRACK_SCRIPT}")

runpy.run_path(str(TRACK_SCRIPT), run_name="__main__")
