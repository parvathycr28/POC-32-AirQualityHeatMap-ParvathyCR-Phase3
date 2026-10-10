
import json
import math
from pathlib import Path
from typing import Any

from fastapi import HTTPException


# intelligence.py is located at <repo>/backend/app/services/
REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS_FILE = (
    REPO_ROOT
    / "data-science"
    / "outputs"
    / "intelligence_results.json"
)

REQUIRED_FIELDS = {
    "result_id",
    "result_type",
    "group_key",
    "metric_name",
    "result_value",
    "priority_rank",
    "finding",
    "evidence",
    "quality_status",
    "limitation",
    "method_version",
    "data_version",
    "entity_name",
    "pollutant",
    "is_synthetic",
}

ALLOWED_QUALITY_STATUSES = {"validated", "conditional", "rejected"}


def get_intelligence_results() -> dict[str, Any]:
    """Read and validate the published intelligence result records."""

    if not RESULTS_FILE.is_file():
        raise HTTPException(
            status_code=503,
            detail="The intelligence results file is unavailable.",
        )

    try:
        with RESULTS_FILE.open("r", encoding="utf-8") as file:
            results = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=500,
            detail="The intelligence results file could not be read.",
        ) from error

    if not isinstance(results, list):
        raise HTTPException(
            status_code=500,
            detail="The intelligence results must be a JSON list.",
        )

    seen_ids: set[str] = set()

    for index, record in enumerate(results):
        if not isinstance(record, dict):
            raise HTTPException(
                status_code=500,
                detail=f"Invalid result record at index {index}.",
            )

        missing = REQUIRED_FIELDS - record.keys()
        if missing:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Result record {index} is missing required fields: "
                    f"{', '.join(sorted(missing))}"
                ),
            )

        result_id = record["result_id"]
        if not isinstance(result_id, str) or not result_id.strip():
            raise HTTPException(
                status_code=500,
                detail=f"Invalid result_id at index {index}.",
            )

        if result_id in seen_ids:
            raise HTTPException(
                status_code=500,
                detail=f"Duplicate result_id: {result_id}.",
            )
        seen_ids.add(result_id)

        if record["quality_status"] not in ALLOWED_QUALITY_STATUSES:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid quality status for {result_id}.",
            )

        value = record["result_value"]
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise HTTPException(
                status_code=500,
                detail=f"Invalid numeric result_value for {result_id}.",
            )

        if not isinstance(record["evidence"], list):
            raise HTTPException(
                status_code=500,
                detail=f"Evidence must be a list for {result_id}.",
            )

    return {
        "metadata": {
            "data_version": "phase3-v1.1",
            "method_version": "track-a-comparative-v1.0.0",
            "count": len(results),
            "is_synthetic": True,
            "quality_status": "conditional",
            "description": (
                "Synthetic descriptive comparisons based on the approved "
                "Phase 3 sample. These are not verified real-world "
                "measurements, regulatory assessments, health-risk "
                "assessments, or predictions."
            ),
        },
        "count": len(results),
        "results": results,
    }
