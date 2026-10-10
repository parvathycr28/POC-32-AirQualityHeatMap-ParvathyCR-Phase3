from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/canonical/intelligence_data.csv")
OUTPUT_DIR = Path("data-science/outputs")

EXPECTED_VERSION = "phase3-v1.1"
METHOD_VERSION = "track-a-comparative-v1.0.0"

REQUIRED_COLUMNS = {
    "record_id",
    "record_type",
    "observed_at",
    "entity_id",
    "entity_name",
    "category",
    "subcategory",
    "metric_name",
    "metric_value",
    "metric_unit",
    "source_name",
    "is_synthetic",
    "data_version",
}


def load_and_validate_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Canonical dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    versions = df["data_version"].dropna().unique().tolist()
    if versions != [EXPECTED_VERSION]:
        raise ValueError(
            f"Expected data version {EXPECTED_VERSION}; found {versions}"
        )

    if df["is_synthetic"].isna().any():
        raise ValueError("Synthetic provenance contains missing flags.")

    synthetic_flags = {
        str(value).strip().lower() for value in df["is_synthetic"].unique()
    }
    if synthetic_flags not in ({"true"}, {"1"}):
        raise ValueError(
            f"Expected all records to be synthetic; found {synthetic_flags}"
        )

    if df["record_id"].isna().any() or df["record_id"].duplicated().any():
        raise ValueError("record_id values must be present and unique.")

    if df[list(REQUIRED_COLUMNS)].isna().any().any():
        # Some fields are essential for this analysis and must not be silently
        # imputed or dropped. Fail with a clear message for investigation.
        raise ValueError("A required field contains missing values.")

    df["metric_value"] = pd.to_numeric(df["metric_value"], errors="raise")
    if not df["metric_value"].map(pd.notna).all():
        raise ValueError("metric_value contains missing or invalid values.")

    if not df["metric_value"].map(lambda value: pd.notna(value) and abs(value) != float("inf")).all():
        raise ValueError("metric_value contains non-finite values.")

    if (df["metric_value"] < 0).any():
        raise ValueError("Negative metric_value found; review before aggregation.")

    df["observed_at"] = pd.to_datetime(
        df["observed_at"], errors="raise", utc=True
    )

    # The two pollutant identifiers should agree before aggregation.
    left = df["subcategory"].astype(str).str.strip().str.lower()
    right = df["metric_name"].astype(str).str.strip().str.lower()
    if not left.equals(right):
        raise ValueError("subcategory and metric_name disagree.")

    # Do not average incompatible units for the same pollutant.
    units_per_pollutant = df.groupby("subcategory")["metric_unit"].nunique()
    if (units_per_pollutant > 1).any():
        raise ValueError(
            "Incompatible or inconsistent units found within a pollutant."
        )

    return df


def build_results(df: pd.DataFrame) -> tuple[list[dict], dict]:
    group_keys = ["entity_id", "entity_name", "subcategory", "metric_unit"]

    grouped = (
        df.groupby(
        ["entity_id", "entity_name", "subcategory", "metric_unit"],
        dropna=False,
    )
        
        .agg(
            observation_count=("metric_value", "count"),
            mean_value=("metric_value", "mean"),
            median_value=("metric_value", "median"),
            minimum_value=("metric_value", "min"),
            maximum_value=("metric_value", "max"),
            period_start=("observed_at", "min"),
            period_end=("observed_at", "max"),
        )

        .reset_index()
    )

    pollutant_baselines = (
        df.groupby("subcategory")["metric_value"].mean().to_dict()
    )

    grouped["pollutant_baseline_mean"] = grouped["subcategory"].map(
        pollutant_baselines
    )
    grouped["difference_from_baseline"] = (
        grouped["mean_value"] - grouped["pollutant_baseline_mean"]
    )
    grouped["relative_difference"] = grouped.apply(
        lambda row: (
            row["difference_from_baseline"] / row["pollutant_baseline_mean"]
            if row["pollutant_baseline_mean"] != 0
            else None
        ),
        axis=1,
    )

    # Deterministic ranking: descending city mean, then entity_id ascending.
    grouped = grouped.sort_values(
        ["subcategory", "mean_value", "entity_id"],
        ascending=[True, False, True],
        kind="mergesort",
    )
    grouped["rank_within_pollutant"] = (
        grouped.groupby("subcategory").cumcount() + 1
    )

    generated_at = pd.Timestamp.now(tz="UTC").isoformat()
    results = []

   
    for index, row in enumerate(grouped.to_dict(orient="records"), start=1):
        mean_value = float(row["mean_value"])
        baseline_value = float(row["pollutant_baseline_mean"])
        gap = float(row["difference_from_baseline"])
        rank = int(row["rank_within_pollutant"])
        pollutant = str(row["subcategory"])
        entity_id = str(row["entity_id"])
        entity_name = str(row["entity_name"])
        unit = str(row["metric_unit"])

        category = (
            "above_baseline" if gap > 1e-12
            else "below_baseline" if gap < -1e-12
            else "at_baseline"
        )

        limitation = (
            "Synthetic descriptive comparison only; not a verified real-world "
            "air-quality measurement, regulatory assessment, health-risk "
            "assessment, or prediction."
        )

        results.append({
         # Mandatory standard Intelligence Output Contract fields
            "result_id": f"RES-{index:04d}",
            "result_type": "ranking",
            "record_id": None,
            "entity_id": entity_id,
            "group_key": f"{entity_id}::{pollutant}::{unit}",
            "period_start": pd.Timestamp(row["period_start"]).isoformat(),
            "period_end": pd.Timestamp(row["period_end"]).isoformat(),
            "metric_name": f"{pollutant}_mean",
            "result_value": mean_value,
            "result_unit": unit,
            "result_category": category,
            "priority_rank": rank,
            "finding": (
                f"{entity_name} ranks {rank} for {pollutant} by sampled mean; "
                f"its mean is {gap:.6g} {unit} relative to the pollutant-wide "
                "sample mean baseline."
            ),
            "evidence": [
                {
                    "factor": "observation_count",
                    "value": int(row["observation_count"]),
                },
                {"factor": "mean_value", "value": mean_value},
                {"factor": "median_value", "value": float(row["median_value"])},
                {"factor": "minimum_value", "value": float(row["minimum_value"])},
                {"factor": "maximum_value", "value": float(row["maximum_value"])},
                {"factor": "pollutant_baseline_mean", "value": baseline_value},
                {"factor": "difference_from_baseline", "value": gap},
                {
                    "factor": "relative_difference",
                    "value": (
                        None
                        if pd.isna(row["relative_difference"])
                        else float(row["relative_difference"])
                    ),
                },
                {"factor": "is_synthetic", "value": True},
            ],
            "method_version": METHOD_VERSION,
            "data_version": EXPECTED_VERSION,
            "generated_at": generated_at,
            "quality_status": "conditional",
            "limitation": limitation,

            # Preserve existing Track A-specific fields for compatibility
            "entity_name": entity_name,
            "pollutant": pollutant,
            "metric_unit": unit,
            "observation_count": int(row["observation_count"]),
            "mean_value": mean_value,
            "median_value": float(row["median_value"]),
            "minimum_value": float(row["minimum_value"]),
            "maximum_value": float(row["maximum_value"]),
            "pollutant_baseline_mean": baseline_value,
            "difference_from_baseline": gap,
            "relative_difference": (
                None
                if pd.isna(row["relative_difference"])
                else float(row["relative_difference"])
            ),
            "rank_within_pollutant": rank,
            "is_synthetic": True,
            "interpretation": limitation,
        })


    summary = {
        "project_id": "POC-32",
        "project_title": "Infocreon Aether Pulse Air Quality Heatmap",
        "approved_track": "Track A — Comparative Intelligence",
        "primary_analytical_question": (
            "Within each pollutant, how do sampled city measurements compare "
            "with each other and with that pollutant's overall mean?"
        ),
        "decision_to_be_supported": (
            "Explore descriptive differences among synthetic city-pollutant "
            "groups; no operational or public-health decision is supported."
        ),
        "data_version": EXPECTED_VERSION,
        "method_version": METHOD_VERSION,
        "result_count": len(results),
        "key_findings": [],
        "priority_items": [],
        "validation_result": "PENDING",
        "important_limitations": [
            "All observations are synthetic.",
            "Only three timestamps across one calendar date are represented "
            "in the Post #2 evidence.",
            "Rankings are descriptive and do not establish real-world "
            "air-quality conditions or health risk.",
            "The pollutant-wide mean is a baseline, not a regulatory threshold.",
        ],
        "generated_at": generated_at,
    }

    for pollutant in sorted(grouped["subcategory"].unique()):
        subset = grouped[grouped["subcategory"] == pollutant]
        highest = subset.iloc[0]
        lowest = subset.iloc[-1]
        baseline = float(pollutant_baselines[pollutant])
        summary["key_findings"].append(
            {
                "pollutant": str(pollutant),
                "highest_sampled_city_mean": str(highest["entity_name"]),
                "highest_mean_value": float(highest["mean_value"]),
                "lowest_sampled_city_mean": str(lowest["entity_name"]),
                "lowest_mean_value": float(lowest["mean_value"]),
                "pollutant_baseline_mean": baseline,
                "finding_scope": "Synthetic descriptive comparison only",
            }
        )

    return results, summary


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_and_validate_data()
    results, summary = build_results(df)

    (OUTPUT_DIR / "intelligence_results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "intelligence_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )

    print(f"Input rows: {len(df)}")
    print(f"Data version: {EXPECTED_VERSION}")
    print(f"Result groups: {len(results)}")
    print(f"Method version: {METHOD_VERSION}")
    print("Generated intelligence_results.json and intelligence_summary.json")


if __name__ == "__main__":
    main()
