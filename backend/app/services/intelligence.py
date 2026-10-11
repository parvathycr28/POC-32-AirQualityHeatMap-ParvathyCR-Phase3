
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException


# Repository paths used when explicit environment variables are not set.
REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "data-science" / "outputs"

# Allow Docker Compose or another deployment environment to specify
# the exact paths of the published analytical output files.
RESULTS_FILE = Path(
    os.environ.get(
        "INTELLIGENCE_RESULTS_FILE",
        str(OUTPUT_DIR / "intelligence_results.json"),
    )
)

SUMMARY_FILE = Path(
    os.environ.get(
        "INTELLIGENCE_SUMMARY_FILE",
        str(OUTPUT_DIR / "intelligence_summary.json"),
    )
)

EXPECTED_DATA_VERSION = "phase3-v1.1"
EXPECTED_METHOD_VERSION = "track-a-comparative-v1.0.0"
EXPECTED_RESULT_COUNT = 32

REQUIRED_RESULT_FIELDS = {
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
    "generated_at",
    "entity_name",
    "pollutant",
    "is_synthetic",
}

REQUIRED_SUMMARY_FIELDS = {
    "project_id",
    "project_title",
    "approved_track",
    "primary_analytical_question",
    "decision_to_be_supported",
    "data_version",
    "method_version",
    "result_count",
    "key_findings",
    "priority_items",
    "validation_result",
    "important_limitations",
    "generated_at",
}

ALLOWED_QUALITY_STATUSES = {
    "validated",
    "conditional",
    "rejected",
}

# Operational freshness threshold; this is not an analytical validity score.
STALE_AFTER_HOURS = 168


def _fail(message: str, status_code: int = 500) -> None:
    """Raise an HTTP error with a clear diagnostic message."""
    raise HTTPException(
        status_code=status_code,
        detail=message,
    )


def _read_json(path: Path, label: str) -> Any:
    """Read a JSON file and return its decoded contents."""
    if not path.is_file():
        _fail(
            f"The {label} file is unavailable at the configured path.",
            503,
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"The {label} file could not be read as valid JSON."
            ),
        ) from error


def _parse_timestamp(value: Any, label: str) -> datetime:
    """Parse an ISO 8601 timestamp and require timezone information."""
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label} must be an ISO 8601 timestamp.")

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        _fail(f"{label} must be a valid ISO 8601 timestamp.")

    if parsed.tzinfo is None:
        _fail(f"{label} must include a timezone.")

    return parsed.astimezone(timezone.utc)


def _validate_summary(summary: Any) -> dict[str, Any]:
    """Validate the approved analytical summary before returning it."""
    if not isinstance(summary, dict):
        _fail(
            "The intelligence summary must be a JSON object."
        )

    missing = REQUIRED_SUMMARY_FIELDS - summary.keys()

    if missing:
        _fail(
            "The intelligence summary is missing required fields: "
            + ", ".join(sorted(missing))
        )

    required_string_fields = {
        "project_id",
        "project_title",
        "approved_track",
        "primary_analytical_question",
        "decision_to_be_supported",
        "data_version",
        "method_version",
        "validation_result",
        "generated_at",
    }

    for field in required_string_fields:
        value = summary[field]

        if not isinstance(value, str) or not value.strip():
            _fail(
                f"The summary field '{field}' is missing or invalid."
            )

    if summary["data_version"] != EXPECTED_DATA_VERSION:
        _fail(
            "The summary data version is not the approved version."
        )

    if summary["method_version"] != EXPECTED_METHOD_VERSION:
        _fail(
            "The summary method version is not the approved version."
        )

    if summary["validation_result"] != "PASS":
        _fail(
            "The analytical summary has not passed validation."
        )

    if (
        type(summary["result_count"]) is not int
        or summary["result_count"] != EXPECTED_RESULT_COUNT
    ):
        _fail(
            "The summary result count does not match the approved count."
        )

    if not isinstance(summary["key_findings"], list):
        _fail("Summary key_findings must be an array.")

    if not isinstance(summary["priority_items"], list):
        _fail("Summary priority_items must be an array.")

    if not isinstance(summary["important_limitations"], list):
        _fail(
            "Summary important_limitations must be an array."
        )

    if not all(
        isinstance(item, str) and item.strip()
        for item in summary["important_limitations"]
    ):
        _fail(
            "Summary important_limitations contains an invalid item."
        )

    _parse_timestamp(
        summary["generated_at"],
        "Summary generated_at",
    )

    return summary


def _validate_results(
    results: Any,
    summary: dict[str, Any],
) -> list[dict[str, Any]]:
    """Validate result records against the approved summary contract."""
    if not isinstance(results, list):
        _fail(
            "The intelligence results must be a JSON array."
        )

    if len(results) != EXPECTED_RESULT_COUNT:
        _fail(
            "The result array does not match the approved result count."
        )

    if len(results) != summary["result_count"]:
        _fail(
            "The result array and summary result count do not match."
        )

    summary_timestamp = _parse_timestamp(
        summary["generated_at"],
        "Summary generated_at",
    )

    seen_ids: set[str] = set()

    for index, record in enumerate(results):
        if not isinstance(record, dict):
            _fail(
                f"Result record {index} must be a JSON object."
            )

        missing = REQUIRED_RESULT_FIELDS - record.keys()

        if missing:
            _fail(
                f"Result record {index} is missing required fields: "
                + ", ".join(sorted(missing))
            )

        result_id = record["result_id"]

        if not isinstance(result_id, str) or not result_id.strip():
            _fail(
                f"Result record {index} has an invalid result_id."
            )

        if result_id in seen_ids:
            _fail(f"Duplicate result_id: {result_id}.")

        seen_ids.add(result_id)

        required_string_fields = (
            "result_type",
            "group_key",
            "metric_name",
            "finding",
            "quality_status",
            "limitation",
            "method_version",
            "data_version",
            "generated_at",
            "entity_name",
            "pollutant",
        )

        for field in required_string_fields:
            value = record[field]

            if not isinstance(value, str) or not value.strip():
                _fail(
                    f"{result_id} has an invalid {field}."
                )

        if record["result_type"] != "ranking":
            _fail(
                f"{result_id} has an unsupported result_type."
            )

        if record["data_version"] != summary["data_version"]:
            _fail(
                f"{result_id} has a mismatched data version."
            )

        if record["method_version"] != summary["method_version"]:
            _fail(
                f"{result_id} has a mismatched method version."
            )

        if record["quality_status"] not in ALLOWED_QUALITY_STATUSES:
            _fail(
                f"{result_id} has an invalid quality status."
            )

        if record["is_synthetic"] is not True:
            _fail(
                f"{result_id} does not declare the approved "
                "synthetic status."
            )

        value = record["result_value"]

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            _fail(
                f"{result_id} has an invalid numeric result_value."
            )

        rank = record["priority_rank"]

        if type(rank) is not int or rank < 1:
            _fail(
                f"{result_id} has an invalid priority_rank."
            )

        evidence = record["evidence"]

        if not isinstance(evidence, list) or not evidence:
            _fail(
                f"{result_id} must contain non-empty evidence."
            )

        for item in evidence:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("factor"), str)
                or not item["factor"].strip()
                or "value" not in item
            ):
                _fail(
                    f"{result_id} contains a malformed evidence item."
                )

            evidence_value = item["value"]

            if (
                evidence_value is not None
                and not isinstance(
                    evidence_value,
                    (str, int, float, bool),
                )
            ):
                _fail(
                    f"{result_id} contains an unsupported evidence value."
                )

            if (
                isinstance(evidence_value, float)
                and not math.isfinite(evidence_value)
            ):
                _fail(
                    f"{result_id} contains a non-finite evidence value."
                )

        record_timestamp = _parse_timestamp(
            record["generated_at"],
            f"{result_id} generated_at",
        )

        if record_timestamp != summary_timestamp:
            _fail(
                f"{result_id} generated_at does not match "
                "the summary timestamp."
            )

    return results


def get_intelligence_summary() -> dict[str, Any]:
    """Return the approved summary only when its contract is valid."""
    summary = _read_json(
        SUMMARY_FILE,
        "intelligence summary",
    )

    return _validate_summary(summary)


def get_intelligence_results() -> dict[str, Any]:
    """Validate results against the approved summary before returning them."""
    summary = get_intelligence_summary()

    raw_results = _read_json(
        RESULTS_FILE,
        "intelligence results",
    )

    results = _validate_results(
        raw_results,
        summary,
    )

    generated_at = _parse_timestamp(
        summary["generated_at"],
        "Summary generated_at",
    )

    age_hours = max(
        0.0,
        (
            datetime.now(timezone.utc) - generated_at
        ).total_seconds() / 3600,
    )

    freshness_status = (
        "STALE"
        if age_hours > STALE_AFTER_HOURS
        else "CURRENT"
    )

    quality_statuses = sorted(
        {
            record["quality_status"]
            for record in results
        }
    )

    quality_status = (
        quality_statuses[0]
        if len(quality_statuses) == 1
        else "mixed"
    )

    return {
        "metadata": {
            "data_version": summary["data_version"],
            "method_version": summary["method_version"],
            "count": len(results),
            "is_synthetic": True,
            "quality_status": quality_status,
            "description": summary["decision_to_be_supported"],
            "approved_track": summary["approved_track"],
            "generated_at": summary["generated_at"],
            "freshness_status": freshness_status,
            "freshness_age_hours": round(age_hours, 2),
            "stale_after_hours": STALE_AFTER_HOURS,
            "validation_result": summary["validation_result"],
        },
        "count": len(results),
        "results": results,
    }