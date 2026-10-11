
"""Build traceable evidence packages from approved intelligence outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _first_available(*values: Any) -> Any:
    """Return the first value that is not None or an empty string."""
    for value in values:
        if value is not None and value != "":
            return value
    return None


def _find_metadata(
    summary: dict[str, Any] | None,
    *keys: str,
) -> Any:
    """Read metadata from the summary or its known metadata containers."""
    if not isinstance(summary, dict):
        return None

    containers = [summary]

    for container_key in ("metadata", "quality", "data_quality", "provenance"):
        value = summary.get(container_key)
        if isinstance(value, dict):
            containers.append(value)

    for container in containers:
        for key in keys:
            value = container.get(key)
            if value is not None and value != "":
                return value

    return None


def build_evidence_package(
    *,
    question: str,
    intent: str,
    result_records: list[dict[str, Any]],
    summary: dict[str, Any] | None = None,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a structured evidence package for one supported assistant request.

    Values are copied from approved output records or metadata.
    This function does not compute new findings, rankings, or predictions.
    """
    parameters = parameters or {}
    selected_records: list[dict[str, Any]] = []

    for record in result_records:
        if not isinstance(record, dict):
            continue

        selected_records.append({
            "result_id": record.get("result_id"),
            "result_type": record.get("result_type"),
            "record_id": record.get("record_id"),
            "entity_id": record.get("entity_id"),
            "group_key": record.get("group_key"),
            "period_start": record.get("period_start"),
            "period_end": record.get("period_end"),
            "metric_name": record.get("metric_name"),
            "result_value": record.get("result_value"),
            "result_unit": record.get("result_unit"),
            "result_category": record.get("result_category"),
            "priority_rank": record.get("priority_rank"),
            "finding": record.get("finding"),
            "evidence": record.get("evidence"),
            "quality_status": record.get("quality_status"),
            "limitation": record.get("limitation"),
            "data_version": record.get("data_version"),
            "method_version": record.get("method_version"),
            "generated_at": record.get("generated_at"),
        })

    versions = sorted({
        str(record["data_version"])
        for record in selected_records
        if record.get("data_version") not in (None, "")
    })
    method_versions = sorted({
        str(record["method_version"])
        for record in selected_records
        if record.get("method_version") not in (None, "")
    })

    quality_values = [
        record.get("quality_status")
        for record in selected_records
        if record.get("quality_status") not in (None, "")
    ]

    limitations = []
    for record in selected_records:
        value = record.get("limitation")
        if value is None or value == "":
            continue
        if isinstance(value, list):
            limitations.extend(str(item) for item in value if item)
        else:
            limitations.append(str(value))

    summary_quality = _find_metadata(
        summary,
        "quality_status",
        "validation_status",
        "status",
    )
    summary_limitation = _find_metadata(
        summary,
        "limitation",
        "limitations",
    )

    if isinstance(summary_limitation, list):
        limitations.extend(str(item) for item in summary_limitation if item)
    elif summary_limitation:
        limitations.append(str(summary_limitation))

    # Preserve order while removing duplicate limitation messages.
    limitations = list(dict.fromkeys(limitations))

    generated_at_values = [
        record.get("generated_at")
        for record in selected_records
        if record.get("generated_at") not in (None, "")
    ]

    quality_status = (
        quality_values[0]
        if quality_values and len(set(map(str, quality_values))) == 1
        else summary_quality
    )

    return {
        "evidence_package_version": "grounded-evidence-v1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "intent": intent,
        "parameters": parameters,
        "source": {
            "name": "approved_intelligence_results",
            "record_count": len(selected_records),
            "result_ids": [
                record["result_id"]
                for record in selected_records
                if record.get("result_id")
            ],
            "data_versions": versions,
            "method_versions": method_versions,
            "generated_at_values": generated_at_values,
        },
        "quality": {
            "quality_status": quality_status,
            "record_quality_statuses": quality_values,
            "limitations": limitations,
            "quality_metadata_available": bool(
                quality_values or summary_quality
            ),
        },
        "records": selected_records,
        "checks": {
            "has_records": bool(selected_records),
            "has_result_ids": bool(
                selected_records
                and all(record.get("result_id") for record in selected_records)
            ),
            "has_data_version": bool(versions),
            "has_method_version": bool(method_versions),
            "has_metric_values": bool(
                selected_records
                and all(record.get("result_value") is not None
                        for record in selected_records)
            ),
        },
    }

