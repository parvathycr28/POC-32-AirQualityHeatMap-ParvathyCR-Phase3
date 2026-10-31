
import json
from pathlib import Path
from typing import Any


class IntelligenceDataError(Exception):
    """Raised when approved intelligence data cannot be used safely."""


def _read_json(path: str | Path) -> Any:
    """Read an approved JSON file and report safe, controlled errors."""
    path = Path(path)

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise IntelligenceDataError(
            "Approved intelligence file is missing."
        ) from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise IntelligenceDataError(
            "Approved intelligence file is unreadable or invalid JSON."
        ) from exc


def load_results(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate existing intelligence results without recalculating them."""
    payload = _read_json(path)

    if not isinstance(payload, list):
        raise IntelligenceDataError(
            "Intelligence results must be a JSON array."
        )

    if not all(isinstance(item, dict) for item in payload):
        raise IntelligenceDataError(
            "An intelligence result has an invalid structure."
        )

    required = {
        "result_id",
        "group_key",
        "metric_name",
        "result_value",
        "data_version",
        "method_version",
    }

    for item in payload:
        if not required.issubset(item):
            raise IntelligenceDataError(
                "An intelligence result is missing required fields."
            )

    result_ids = [item["result_id"] for item in payload]

    if len(result_ids) != len(set(result_ids)):
        raise IntelligenceDataError("Duplicate result IDs detected.")

    data_versions = {item["data_version"] for item in payload}
    method_versions = {item["method_version"] for item in payload}

    if len(data_versions) != 1 or len(method_versions) != 1:
        raise IntelligenceDataError(
            "Mixed data or method versions detected."
        )

    return payload


def load_summary(path: str | Path) -> Any:
    """Load the existing intelligence summary."""
    return _read_json(path)


def get_result_evidence(
    results: list[dict],
    result_id: str,
) -> dict | None:
    matches = [
        item for item in results
        if item.get("result_id") == result_id
    ]
    return matches[0] if len(matches) == 1 else None


def get_highest_city(
    results: list[dict],
    pollutant: str,
) -> dict | None:
    """
    Retrieve the existing rank-1 result for a pollutant.
    Do not calculate a new ranking here.
    """
    normalized = pollutant.strip().casefold()

    matches = [
        item for item in results
        if normalized in str(item.get("group_key", "")).casefold()
        and item.get("priority_rank") == 1
    ]

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        raise IntelligenceDataError(
            "Multiple rank-1 results match; a unique result "
            "cannot be selected safely."
        )

    return None


def compare_cities(
    results: list[dict],
    pollutant: str,
    city_a: str,
    city_b: str,
) -> list[dict]:
    normalized_pollutant = pollutant.strip().casefold()
    normalized_cities = {
        city_a.strip().casefold(),
        city_b.strip().casefold(),
    }

    if len(normalized_cities) != 2:
        raise ValueError("Choose two different cities.")

    matches = [
        item for item in results
        if normalized_pollutant in str(item.get("group_key", "")).casefold()
        and str(item.get("entity_id", "")).casefold() in normalized_cities
    ]

    found_cities = {
        str(item.get("entity_id", "")).casefold()
        for item in matches
    }

    if found_cities != normalized_cities:
        return []

    metrics = {item.get("metric_name") for item in matches}
    units = {item.get("result_unit") for item in matches}

    if len(metrics) != 1 or len(units) > 1:
        raise IntelligenceDataError(
            "The selected cities do not have safely comparable result metrics."
        )

    if len(matches) != 2:
        raise IntelligenceDataError(
            "Expected exactly two comparable city results."
        )

    requested_order = {
        city_a.strip().casefold(): 0,
        city_b.strip().casefold(): 1,
    }

    return sorted(
        matches,
        key=lambda item: requested_order[
            str(item.get("entity_id", "")).casefold()
        ],
    )


def get_summary_results(
    results: list[dict],
    limit: int = 10,
) -> list[dict]:
    if not 1 <= limit <= 10:
        raise ValueError("Summary limit must be between 1 and 10.")

    return results[:limit]
