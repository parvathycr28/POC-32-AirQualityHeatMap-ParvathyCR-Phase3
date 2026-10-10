import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "data-science" / "outputs"

RESULTS = OUTPUTS / "intelligence_results.json"
SUMMARY = OUTPUTS / "intelligence_summary.json"

EXPECTED_DATA_VERSION = "phase3-v1.1"
EXPECTED_METHOD_VERSION = "track-a-comparative-v1.0.0"


def main():
    if not RESULTS.exists() or not SUMMARY.exists():
        raise FileNotFoundError(
            "Run run_analytical_track.py before exporting results."
        )

    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    if not isinstance(results, list):
        raise ValueError("intelligence_results.json must contain a JSON list.")

    for item in results:
        if item.get("data_version") != EXPECTED_DATA_VERSION:
            raise ValueError("Unexpected data_version in a result.")
        if item.get("method_version") != EXPECTED_METHOD_VERSION:
            raise ValueError("Unexpected method_version in a result.")

    if summary.get("data_version") != EXPECTED_DATA_VERSION:
        raise ValueError("Unexpected data_version in summary.")
    if summary.get("method_version") != EXPECTED_METHOD_VERSION:
        raise ValueError("Unexpected method_version in summary.")
    if summary.get("result_count") != len(results):
        raise ValueError("Summary result_count does not match results.")

    print("Export verification: PASS")
    print("Result records:", len(results))
    print("Data version:", EXPECTED_DATA_VERSION)
    print("Method version:", EXPECTED_METHOD_VERSION)
    print("Results:", RESULTS.relative_to(ROOT))
    print("Summary:", SUMMARY.relative_to(ROOT))


if __name__ == "__main__":
    main()
