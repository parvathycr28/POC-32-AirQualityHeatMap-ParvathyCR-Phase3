import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILE = (
    ROOT / "data-science" / "outputs" / "intelligence_results.json"
)
SUMMARY_FILE = (
    ROOT / "data-science" / "outputs" / "intelligence_summary.json"
)


def distinct_values(records, field):
    return sorted({
        str(record[field]).strip()
        for record in records
        if record.get(field) is not None
        and str(record[field]).strip()
    })


def main():
    if not SOURCE_FILE.is_file():
        raise FileNotFoundError(
            f"Results file not found: {SOURCE_FILE}"
        )

    with SOURCE_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    # The actual source is a JSON array of result records.
    if not isinstance(records, list):
        raise ValueError(
            "Expected intelligence_results.json to contain a JSON array."
        )

    if not all(isinstance(record, dict) for record in records):
        raise ValueError(
            "Every item in the results array must be a JSON object."
        )

    if not records:
        raise ValueError(
            "The results array is empty; refusing to generate a misleading summary."
        )

    result_type_counts = Counter(
        str(record["result_type"])
        for record in records
        if record.get("result_type") is not None
    )

    category_counts = Counter(
        str(record["result_category"])
        for record in records
        if record.get("result_category") is not None
    )

    versions = {
        "data_versions": distinct_values(records, "data_version"),
        "method_versions": distinct_values(records, "method_version"),
        "quality_statuses": distinct_values(records, "quality_status"),
    }

    synthetic_flags = sorted({
        record["is_synthetic"]
        for record in records
        if isinstance(record.get("is_synthetic"), bool)
    })

    ranked_records = [
        record for record in records
        if isinstance(record.get("priority_rank"), (int, float))
        and not isinstance(record.get("priority_rank"), bool)
    ]
    ranked_records.sort(key=lambda record: record["priority_rank"])

    example_fields = (
        "result_id",
        "result_type",
        "entity_name",
        "pollutant",
        "metric_name",
        "result_value",
        "result_unit",
        "priority_rank",
        "finding",
        "limitation",
    )

    priority_examples = [
        {
            field: record[field]
            for field in example_fields
            if field in record
        }
        for record in ranked_records[:5]
    ]

    summary = {
        "summary_schema_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "file": "data-science/outputs/intelligence_results.json",
            "source_format": "JSON array of result records",
        },
        "versions": versions,
        "quality": {
            "is_synthetic_values": synthetic_flags,
            "record_count": len(records),
            "contains_conditional_quality": (
                "conditional" in versions["quality_statuses"]
            ),
        },
        "overview": {
            "result_count": len(records),
            "entity_count": len(distinct_values(records, "entity_name")),
            "entities": distinct_values(records, "entity_name"),
            "pollutant_count": len(distinct_values(records, "pollutant")),
            "pollutants": distinct_values(records, "pollutant"),
            "result_type_counts": dict(sorted(result_type_counts.items())),
            "result_category_counts": dict(sorted(category_counts.items())),
        },
        "priority_examples": priority_examples,
        "limitations": (
            "This summary is derived from the published intelligence result "
            "records. Where results are synthetic, they are descriptive "
            "comparisons and are not verified real-world measurements, "
            "regulatory assessments, health-risk assessments, or predictions."
        ),
    }

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY_FILE.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)
        file.write("\n")

    print("Intelligence summary generated successfully.")
    print(f"Source records: {len(records)}")
    print(f"Entities: {summary['overview']['entity_count']}")
    print(f"Pollutants: {summary['overview']['pollutant_count']}")
    print(f"Data versions: {versions['data_versions']}")
    print(f"Method versions: {versions['method_versions']}")
    print(f"Output: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
