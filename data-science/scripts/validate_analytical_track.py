from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pandas as pd

DATA = Path("data/canonical/intelligence_data.csv")
RESULTS = Path("data-science/outputs/intelligence_results.json")
SUMMARY = Path("data-science/outputs/intelligence_summary.json")
METRICS = Path("data-science/outputs/validation_metrics.json")
WEAK_CASES = Path("data-science/outputs/weak_case_review.json")

TRACK_SCRIPT = (
    "data-science/scripts/track-specific/"
    "track_a_comparative_intelligence.py"
)

def main() -> None:
    df = pd.read_csv(DATA)
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    checks = {}
    issues = []

    checks["canonical_rows_96"] = len(df) == 96
    checks["canonical_columns_20"] = len(df.columns) == 20
    checks["expected_data_version"] = (
        set(df["data_version"].dropna()) == {"phase3-v1.1"}
    )
    checks["all_records_synthetic"] = (
        df["is_synthetic"].astype(str).str.lower().eq("true").all()
    )
    checks["unique_record_ids"] = (
        df["record_id"].notna().all() and df["record_id"].is_unique
    )

    expected_groups = (
        df.groupby(["entity_id", "entity_name", "subcategory", "metric_unit"])
        .size()
        .reset_index(name="count")
    )
    expected_group_count = len(expected_groups)
    checks["expected_group_count"] = len(results) == expected_group_count

    result_by_key = {
        (r["entity_id"], r["pollutant"], r["metric_unit"]): r
        for r in results
    }

    # Independent calculation from the source CSV.
    reference = (
        df.groupby(["entity_id", "subcategory", "metric_unit"])["metric_value"]
        .mean()
        .to_dict()
    )
    baseline = df.groupby("subcategory")["metric_value"].mean().to_dict()

    max_mean_error = 0.0
    max_gap_error = 0.0
    group_size_errors = []

    for row in results:
        key = (row["entity_id"], row["pollutant"], row["metric_unit"])
        ref_key = (row["entity_id"], row["pollutant"], row["metric_unit"])

        if key not in reference:
            issues.append(f"Unexpected result group: {key}")
            continue

        calculated_mean = float(reference[ref_key])
        calculated_baseline = float(baseline[row["pollutant"]])
        calculated_gap = calculated_mean - calculated_baseline

        max_mean_error = max(
            max_mean_error,
            abs(float(row["mean_value"]) - calculated_mean),
        )
        max_gap_error = max(
            max_gap_error,
            abs(float(row["difference_from_baseline"]) - calculated_gap),
        )

        source_count = int(
            (
                (df["entity_id"] == row["entity_id"])
                & (df["subcategory"] == row["pollutant"])
                & (df["metric_unit"] == row["metric_unit"])
            ).sum()
        )
        if int(row["observation_count"]) != source_count:
            group_size_errors.append(key)

    checks["independent_means_match"] = max_mean_error < 1e-9
    checks["independent_baseline_gaps_match"] = max_gap_error < 1e-9
    checks["group_sizes_match"] = len(group_size_errors) == 0
    checks["result_version_consistent"] = all(
        r.get("data_version") == "phase3-v1.1" for r in results
    )
    checks["method_version_present"] = all(
        r.get("method_version") == "track-a-comparative-v1.0.0"
        for r in results
    )
    checks["summary_result_count_matches"] = (
        summary.get("result_count") == len(results)
    )
    checks["summary_track_is_track_a"] = (
        summary.get("approved_track") == "Track A — Comparative Intelligence"
    )

    # Ranking order must be descending within pollutant; ties are deterministic.
    ranking_errors = []
    for pollutant in sorted({r["pollutant"] for r in results}):
        subset = [r for r in results if r["pollutant"] == pollutant]
        ordered = sorted(
            subset,
            key=lambda r: (
                -float(r["mean_value"]),
                str(r["entity_id"]),
            ),
        )
        if [r["entity_id"] for r in subset] != [
            r["entity_id"] for r in ordered
        ]:
            ranking_errors.append(pollutant)
        if [r["rank_within_pollutant"] for r in subset] != list(
            range(1, len(subset) + 1)
        ):
            ranking_errors.append(f"{pollutant}: rank sequence")

    checks["ranking_order_and_ties"] = not ranking_errors

    for name, passed in checks.items():
        if not passed:
            issues.append(name)

    # Sensitivity check: leave out one timestamp at a time and recompute ranks.
    df["observed_at"] = pd.to_datetime(df["observed_at"], utc=True)
    timestamps = sorted(df["observed_at"].dropna().unique())
    sensitivity = []

    for timestamp in timestamps:
        reduced = df[df["observed_at"] != timestamp]
        reduced_means = (
            reduced.groupby(["entity_id", "subcategory"])["metric_value"]
            .mean()
            .reset_index()
        )
        for pollutant in sorted(reduced_means["subcategory"].unique()):
            sub = reduced_means[reduced_means["subcategory"] == pollutant]
            sub = sub.sort_values(
                ["metric_value", "entity_id"],
                ascending=[False, True],
                kind="mergesort",
            )
            new_order = sub["entity_id"].astype(str).tolist()
            full_order = [
                r["entity_id"]
                for r in results
                if r["pollutant"] == pollutant
            ]
            changed = new_order != full_order
            sensitivity.append({
                "omitted_timestamp": str(timestamp),
                "pollutant": str(pollutant),
                "ranking_changed": changed,
                "interpretation": (
                    "Sensitivity warning; not a model-validation score."
                ),
            })

    weak_cases = {
        "data_version": "phase3-v1.1",
        "method_version": "track-a-comparative-v1.0.0",
        "review_type": "Descriptive weak-case and limitation review",
        "cases": [
            {
                "case": "Synthetic provenance",
                "finding": "All records are synthetic; rankings are not real-world rankings.",
                "severity": "critical_interpretation_limit",
            },
            {
                "case": "Limited temporal coverage",
                "finding": "Only three timestamps across one calendar date are described in Post #2 evidence.",
                "severity": "high",
            },
            {
                "case": "Ranking sensitivity",
                "finding": "Leave-one-timestamp-out rankings are recorded below for review.",
                "severity": "review_required",
            },
            {
                "case": "Baseline interpretation",
                "finding": "The pollutant-wide mean is descriptive and is not a regulatory threshold.",
                "severity": "interpretation_limit",
            },
        ],
        "timestamp_sensitivity": sensitivity,
        "known_limitations": [
            "No inference about verified real-world air quality.",
            "No causal, health-risk, regulatory, or predictive claims.",
            "Small synthetic sample with limited temporal depth.",
        ],
    }

    metrics = {
        "data_version": "phase3-v1.1",
        "method_version": "track-a-comparative-v1.0.0",
        "input_rows": len(df),
        "input_columns": len(df.columns),
        "expected_group_count": expected_group_count,
        "actual_result_count": len(results),
        "maximum_absolute_mean_error": max_mean_error,
        "maximum_absolute_baseline_gap_error": max_gap_error,
        "group_size_errors": group_size_errors,
        "ranking_errors": ranking_errors,
        "checks": checks,
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "issues": issues,
        "timestamp_sensitivity_cases": len(sensitivity),
        "validation_result": "PASS" if all(checks.values()) else "FAIL",
    }

    METRICS.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False, allow_nan=False, default=lambda value: value.item() if hasattr(value, "item") else str(value)),
        encoding="utf-8",
    )
    WEAK_CASES.write_text(
        json.dumps(weak_cases, indent=2, ensure_ascii=False, allow_nan=False, default=lambda value: value.item() if hasattr(value, "item") else str(value)),
        encoding="utf-8",
    )

    # Update summary from actual validation, not a manually entered status.
    summary["validation_result"] = metrics["validation_result"]
    SUMMARY.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False, default=lambda value: value.item() if hasattr(value, "item") else str(value)),
        encoding="utf-8",
    )

    print(json.dumps(metrics, indent=2, ensure_ascii=False, default=lambda value: value.item() if hasattr(value, "item") else str(value)))
    if not all(checks.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
