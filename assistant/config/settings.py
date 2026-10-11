
from pathlib import Path
import os

# Resolve the repository root from this file:
# assistant/config/settings.py -> repository root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_FILE = Path(
    os.getenv(
        "INTELLIGENCE_RESULTS_FILE",
        PROJECT_ROOT / "data-science" / "outputs" / "intelligence_results.json",
    )
)

SUMMARY_FILE = Path(
    os.getenv(
        "INTELLIGENCE_SUMMARY_FILE",
        PROJECT_ROOT / "data-science" / "outputs" / "intelligence_summary.json",
    )
)

VALIDATION_FILE = Path(
    os.getenv(
        "INTELLIGENCE_VALIDATION_FILE",
        PROJECT_ROOT / "data-science" / "outputs" / "validation_metrics.json",
    )
)

MAX_QUESTION_LENGTH = 500
MAX_SUMMARY_RESULTS = 10
