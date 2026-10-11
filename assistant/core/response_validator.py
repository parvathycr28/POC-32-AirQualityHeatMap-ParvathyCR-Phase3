
"""Validate evidence packages before producing grounded answers."""

from __future__ import annotations

from typing import Any


def validate_evidence_package(
    package: dict[str, Any],
    *,
    require_quality_metadata: bool = False,
) -> dict[str, Any]:
    """Validate provenance, versions, and record integrity."""
    errors: list[str] = []
    warnings: list[str] = []

    records = package.get("records")
    source = package.get("source")
    checks = package.get("checks")
    quality = package.get("quality")

    if not isinstance(records, list) or not records:
        errors.append("No approved evidence records were retrieved.")
        records = []

    if not isinstance(source, dict):
        errors.append("Evidence source metadata is missing.")
        source = {}

    if not isinstance(checks, dict):
        errors.append("Evidence checks are missing.")
        checks = {}

    if not isinstance(quality, dict):
        errors.append("Quality metadata is missing.")
        quality = {}

    if not source.get("data_versions"):
        errors.append("Data version is missing.")

    if not source.get("method_versions"):
        errors.append("Method version is missing.")

    if len(source.get("data_versions", [])) > 1:
        errors.append("Evidence contains inconsistent data versions.")

    if len(source.get("method_versions", [])) > 1:
        errors.append("Evidence contains inconsistent method versions.")

    if records and not checks.get("has_result_ids"):
        errors.append("One or more evidence records lack result IDs.")

    if require_quality_metadata and not quality.get(
        "quality_metadata_available"
    ):
        errors.append("Required quality metadata is unavailable.")
    elif not quality.get("quality_metadata_available"):
        warnings.append(
            "Explicit quality status is unavailable; do not imply validation."
        )

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"Evidence record {index} is not an object.")
            continue

        if not record.get("result_id"):
            errors.append(f"Evidence record {index} lacks a result ID.")

        if record.get("result_value") is not None:
            value = record["result_value"]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(
                    f"Evidence record {index} has a non-numeric metric value."
                )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "record_count": len(records),
    }


def validate_answer_records(
    answer_records: list[dict[str, Any]],
    evidence_package: dict[str, Any],
) -> dict[str, Any]:
    """
    Ensure every answer record is backed by an exact source result ID.

    This validates record provenance. It does not attempt to infer whether
    arbitrary natural-language statements are logically entailed.
    """
    evidence_records = evidence_package.get("records", [])
    allowed_ids = {
        record.get("result_id")
        for record in evidence_records
        if isinstance(record, dict) and record.get("result_id")
    }

    errors: list[str] = []

    if not isinstance(answer_records, list) or not answer_records:
        errors.append("The answer contains no source-backed records.")
        answer_records = []

    for index, record in enumerate(answer_records):
        if not isinstance(record, dict):
            errors.append(f"Answer record {index} is not an object.")
            continue

        result_id = record.get("result_id")
        if not result_id or result_id not in allowed_ids:
            errors.append(
                f"Answer record {index} is not backed by retrieved evidence."
            )

    return {
        "valid": not errors,
        "errors": errors,
        "record_count": len(answer_records),
    }

