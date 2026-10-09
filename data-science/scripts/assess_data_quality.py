
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "canonical" / "intelligence_data.csv"
OUTPUT_FILE = ROOT / "data-science" / "outputs" / "quality_assessment.json"


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Canonical dataset not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE, low_memory=False)
    row_count = len(df)

    def count_true(series):
        return int(series.fillna(False).sum())

    def missing_count(column):
        return int(df[column].isna().sum())

    # Completeness
    completeness = {
        column: {
            "missing_count": missing_count(column),
            "missing_percent": round(
                missing_count(column) / row_count * 100, 2
            ) if row_count else 0,
        }
        for column in df.columns
    }

    # Uniqueness
    record_id_duplicates = int(
        df["record_id"].duplicated(keep=False).sum()
    )
    duplicate_full_rows = int(df.duplicated().sum())

    uniqueness = {
        "record_id_duplicate_rows": record_id_duplicates,
        "record_id_unique": bool(
            df["record_id"].notna().all()
            and df["record_id"].is_unique
        ),
        "duplicate_full_rows": duplicate_full_rows,
        "entity_id_unique_count": int(df["entity_id"].nunique(dropna=True)),
    }

    # Numeric validity
    numeric_checks = {}
    for column in ["metric_value", "latitude", "longitude"]:
        numeric = pd.to_numeric(df[column], errors="coerce")
        infinite_count = int(np.isinf(numeric.dropna()).sum())
        parse_failures = int(
            (df[column].notna() & numeric.isna()).sum()
        )
        numeric_checks[column] = {
            "parse_failures": parse_failures,
            "infinite_values": infinite_count,
        }

    latitude = pd.to_numeric(df["latitude"], errors="coerce")
    longitude = pd.to_numeric(df["longitude"], errors="coerce")
    both_coordinates = latitude.notna() & longitude.notna()

    invalid_coordinates = both_coordinates & (
        ~latitude.between(-90, 90)
        | ~longitude.between(-180, 180)
    )

    geographic_validity = {
        "rows_with_both_coordinates": int(both_coordinates.sum()),
        "rows_missing_latitude": int(latitude.isna().sum()),
        "rows_missing_longitude": int(longitude.isna().sum()),
        "invalid_coordinate_rows": int(invalid_coordinates.sum()),
    }

    # Timestamp validity
    timestamps = pd.to_datetime(df["observed_at"], errors="coerce", utc=True)
    timestamp_validity = {
        "valid_timestamps": int(timestamps.notna().sum()),
        "invalid_or_missing_timestamps": int(timestamps.isna().sum()),
        "unique_timestamps": int(timestamps.nunique(dropna=True)),
        "unique_calendar_dates": int(
            timestamps.dropna().dt.strftime("%Y-%m-%d").nunique()
        ),
    }

    # Controlled values and cross-field consistency
    allowed_pollutants = {"pm2.5", "pm10", "no2", "o3"}
    observed_pollutants = (
        df["subcategory"].dropna().astype(str).str.strip().str.lower()
    )
    unexpected_pollutants = sorted(
        set(observed_pollutants.unique()) - allowed_pollutants
    )

    pollutant_counts = {
        str(k): int(v)
        for k, v in observed_pollutants.value_counts().items()
    }

    consistency = {
        "unexpected_pollutant_subcategories": unexpected_pollutants,
        "pollutant_distribution": pollutant_counts,
        "missing_data_version_count": missing_count("data_version"),
        "data_version_distribution": {
            str(k): int(v)
            for k, v in df["data_version"].value_counts(dropna=False).items()
        },
        "missing_source_name_count": missing_count("source_name"),
        "missing_source_record_id_count": missing_count("source_record_id"),
        "missing_metric_unit_count": missing_count("metric_unit"),
        "missing_metric_name_count": missing_count("metric_name"),
    }

    synthetic_values = (
        df["is_synthetic"].astype("string").str.strip().str.lower()
    )
    recognized_boolean_values = {
        "true", "false", "1", "0", "yes", "no"
    }
    unexpected_boolean_values = sorted(
        set(synthetic_values.dropna().unique())
        - recognized_boolean_values
    )

    provenance = {
        "source_name_distribution": {
            str(k): int(v)
            for k, v in df["source_name"].value_counts(dropna=False).items()
        },
        "synthetic_flag_distribution": {
            str(k): int(v)
            for k, v in synthetic_values.value_counts(dropna=False).items()
        },
        "unrecognized_synthetic_flag_values": unexpected_boolean_values,
        "synthetic_flag_missing_count": int(synthetic_values.isna().sum()),
    }

    # This measures missingness and basic structural issues.
    # It cannot independently prove real-world accuracy or representativeness.
    checks = {
        "record_ids_present": bool(df["record_id"].notna().all()),
        "record_ids_unique": uniqueness["record_id_unique"],
        "no_duplicate_full_rows": duplicate_full_rows == 0,
        "timestamps_parseable": timestamp_validity[
            "invalid_or_missing_timestamps"
        ] == 0,
        "no_invalid_coordinate_ranges": geographic_validity[
            "invalid_coordinate_rows"
        ] == 0,
        "no_infinite_numeric_values": all(
            item["infinite_values"] == 0
            for item in numeric_checks.values()
        ),
        "no_numeric_parse_failures": all(
            item["parse_failures"] == 0
            for item in numeric_checks.values()
        ),
        "pollutant_subcategories_expected": len(unexpected_pollutants) == 0,
        "data_version_present": consistency["missing_data_version_count"] == 0,
        "synthetic_flags_recognized": len(unexpected_boolean_values) == 0,
    }

    result = {
        "assessment_name": "Infocreon Canonical Data Quality Assessment",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": "data/canonical/intelligence_data.csv",
        "row_count": int(row_count),
        "column_count": int(len(df.columns)),
        "quality_dimensions": {
            "completeness": {
                "status": "ASSESSED",
                "field_results": completeness,
                "interpretation": (
                    "Review field-level missingness in context; "
                    "some fields may be optional for particular record types."
                ),
            },
            "uniqueness": {
                "status": "PASS" if checks["record_ids_unique"]
                and checks["no_duplicate_full_rows"] else "REVIEW",
                "results": uniqueness,
            },
            "validity": {
                "status": "PASS" if all([
                    checks["timestamps_parseable"],
                    checks["no_invalid_coordinate_ranges"],
                    checks["no_infinite_numeric_values"],
                    checks["no_numeric_parse_failures"],
                    checks["pollutant_subcategories_expected"],
                ]) else "REVIEW",
                "numeric_checks": numeric_checks,
                "geographic_validity": geographic_validity,
                "timestamp_validity": timestamp_validity,
            },
            "consistency": {
                "status": "PASS" if checks["pollutant_subcategories_expected"]
                and checks["data_version_present"] else "REVIEW",
                "results": consistency,
            },
            "provenance": {
                "status": "ASSESSED",
                "results": provenance,
                "limitation": (
                    "Source labels and synthetic flags do not independently "
                    "verify external provenance."
                ),
            },
            "accuracy": {
                "status": "NOT_INDEPENDENTLY_VERIFIED",
                "limitation": (
                    "Accuracy against real-world measurements cannot be "
                    "established from this CSV alone."
                ),
            },
            "representativeness": {
                "status": "REQUIRES_SEPARATE_ASSESSMENT",
                "limitation": (
                    "Coverage counts alone do not prove that the records "
                    "represent real-world cities, time periods, or conditions."
                ),
            },
            "timeliness": {
                "status": "LIMITED_TEMPORAL_COVERAGE"
                if timestamp_validity["unique_calendar_dates"] <= 1
                else "ASSESSED",
                "results": timestamp_validity,
            },
            "reproducibility": {
                "status": "PARTIALLY_ASSESSED",
                "note": (
                    "This assessment is script-generated from the canonical "
                    "CSV. Full reproducibility also depends on versioned "
                    "inputs, scripts, and documented execution."
                ),
            },
        },
        "checks": checks,
        "overall_structural_status": (
            "PASS" if all(checks.values()) else "REVIEW"
        ),
        "interpretation_warning": (
            "A structural PASS does not prove real-world accuracy, "
            "representativeness, or readiness for every analytical track."
        ),
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print("=" * 60)
    print("INFOCREON PHASE 3 — DATA QUALITY ASSESSMENT")
    print("=" * 60)
    print(f"Rows assessed: {row_count}")
    print(f"Unique record IDs: {uniqueness['record_id_unique']}")
    print(f"Duplicate full rows: {duplicate_full_rows}")
    print(f"Invalid coordinate rows: {geographic_validity['invalid_coordinate_rows']}")
    print(f"Unexpected pollutant values: {unexpected_pollutants}")
    print(f"Structural status: {result['overall_structural_status']}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()