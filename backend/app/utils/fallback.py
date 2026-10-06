import json
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "mock_data.json"
)


def load_fallback_data() -> dict:
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)