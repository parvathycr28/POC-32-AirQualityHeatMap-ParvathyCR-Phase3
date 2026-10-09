
import json
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd


# Resolve the repository root from this script's location.
ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "canonical" / "intelligence_data.csv"
OUTPUT_DIR = ROOT / "data-science" / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "canonical_profile.json"

EXPECTED_COLUMNS = [
    "record_id", "record_type", "observed_at", "entity_id",
    "related_entity_id", "entity_name", "category", "subcategory",
    "status", "stage", "metric_name", "metric_value", "metric_unit",
    "text_value", "latitude", "longitude", "source_name",
    "source_record_id", "is_synthetic", "data_version",
]

TEXT_COLUMNS = [
    "record_id", "record_type", "observed_at", "entity_id",
    "related_entity_id", "entity_name", "category", "subcategory",
    "status", "stage", "metric_name", "metric_unit", "text_value",
    "source_name", "source_record_id", "data_version",
]


def json_safe(value):
    """Convert NumPy/Pandas values into JSON-safe Python values."""
    if value is None:
        return None
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return value


def value_counts(series):
    counts = series.astype("string").fillna("<NULL>").value_counts(dropna=False)
    return {str(k): int(v) for k, v in counts.items()}


def field_profile(df, column):
    series = df[column]
    non_null = series.dropna()
    examples = [json_safe(v) for v in non_null.drop_duplicates().head(5).tolist()]

    result = {
        "dtype": str(series.dtype),
        "row_count": int(len(series)),
        "non_null_count": int(series.notna().sum()),
        "null_count": int(series.isna().sum()),
        "null_percent": round(float(series.isna().mean() * 100), 2),
        "unique_non_null_values": int(series.nunique(dropna=True)),
        "examples": examples,
    }

    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce")
        finite = numeric[np.isfinite(numeric)]
        result["numeric_summary"] = {
            "min": json_safe(finite.min()) if len(finite) else None,
            "max": json_safe(finite.max()) if len(finite) else None,
            "mean": json_safe(finite.mean()) if len(finite) else None,
            "median": json_safe(finite.median()) if len(finite) else None,
            "std": json_safe(finite.std()) if len(finite) else None,
            "infinite_count": int(np.isinf(numeric.dropna()).sum()),
            "non_numeric_non_null_count": int(
                (series.notna() & numeric.isna()).sum()
            ),
        }

    if column in TEXT_COLUMNS:
        text = series.dropna().astype(str)
        lengths = text.str.len()
        result["text_summary"] = {
            "empty_string_count": int((text == "").sum()),
            "whitespace_only_count": int(text.str.strip().eq("").sum()),
            "average_length": round(float(lengths.mean()), 2) if len(lengths) else 0,
            "maximum_length": int(lengths.max()) if len(lengths) else 0,
            "case_variants": int(text.str.lower().nunique()),
        }

    return result


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Canonical dataset not found: {DATA_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_FILE, low_memory=False)

    missing_columns = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    unexpected_columns = [c for c in df.columns if c not in EXPECTED_COLUMNS]

    date_values = pd.to_datetime(df["observed_at"], errors="coerce", utc=True)
    valid_dates = date_values.dropna()
    date_strings = valid_dates.dt.strftime("%Y-%m-%d")
    unique_dates = sorted(date_strings.unique().tolist())

    numeric_fields = {}
    for column in ["metric_value", "latitude", "longitude"]:
        numeric = pd.to_numeric(df[column], errors="coerce")
        finite = numeric[np.isfinite(numeric)]
        numeric_fields[column] = {
            "parse_failures_on_non_null": int(
                (df[column].notna() & numeric.isna()).sum()
            ),
            "infinite_count": int(np.isinf(numeric.dropna()).sum()),
            "min": json_safe(finite.min()) if len(finite) else None,
            "max": json_safe(finite.max()) if len(finite) else None,
        }

    lat = pd.to_numeric(df["latitude"], errors="coerce")
    lon = pd.to_numeric(df["longitude"], errors="coerce")
    both_present = lat.notna() & lon.notna()
    valid_coordinates = (
        both_present
        & lat.between(-90, 90)
        & lon.between(-180, 180)
    )

    metric_numeric = pd.to_numeric(df["metric_value"], errors="coerce")
    finite_metrics = metric_numeric[np.isfinite(metric_numeric)]

    if "data_version" in df.columns:
        versions = value_counts(df["data_version"])
    else:
        versions = {}

    profile = {
        "profile_name": "Infocreon Canonical Data Profile",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": "data/canonical/intelligence_data.csv",
        "data_version_distribution": versions,
        "file_size_bytes": DATA_FILE.stat().st_size,
        "file_size_mb": round(DATA_FILE.stat().st_size / (1024 * 1024), 6),
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "expected_columns": EXPECTED_COLUMNS,
        "missing_expected_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "column_order_matches_expected": list(df.columns) == EXPECTED_COLUMNS,
        "record_type_distribution": value_counts(df["record_type"]),
        "entity_count": int(df["entity_id"].nunique(dropna=True)),
        "related_entity_count": int(
            df["related_entity_id"].nunique(dropna=True)
        ),
        "source_name_distribution": value_counts(df["source_name"]),
        "synthetic_distribution": value_counts(df["is_synthetic"]),
        "category_distribution": value_counts(df["category"]),
        "subcategory_distribution": value_counts(df["subcategory"]),
        "status_distribution": value_counts(df["status"]),
        "stage_distribution": value_counts(df["stage"]),
        "metric_name_distribution": value_counts(df["metric_name"]),
        "metric_unit_distribution": value_counts(df["metric_unit"]),
        "metric_value_summary": {
            "numeric_count": int(metric_numeric.notna().sum()),
            "finite_count": int(len(finite_metrics)),
            "invalid_non_numeric_count": int(
                (df["metric_value"].notna() & metric_numeric.isna()).sum()
            ),
            "infinite_count": int(
                np.isinf(metric_numeric.dropna()).sum()
            ),
            "min": json_safe(finite_metrics.min()) if len(finite_metrics) else None,
            "max": json_safe(finite_metrics.max()) if len(finite_metrics) else None,
            "mean": json_safe(finite_metrics.mean()) if len(finite_metrics) else None,
            "median": json_safe(finite_metrics.median()) if len(finite_metrics) else None,
            "std": json_safe(finite_metrics.std()) if len(finite_metrics) else None,
        },
        "date_summary": {
            "row_count": int(len(df)),
            "valid_date_count": int(date_values.notna().sum()),
            "invalid_or_missing_date_count": int(date_values.isna().sum()),
            "unique_timestamps": int(valid_dates.nunique()),
            "unique_calendar_dates": int(len(unique_dates)),
            "minimum_timestamp": valid_dates.min().isoformat() if len(valid_dates) else None,
            "maximum_timestamp": valid_dates.max().isoformat() if len(valid_dates) else None,
            "calendar_dates": unique_dates,
            "rows_per_calendar_date": {
                str(k): int(v) for k, v in date_strings.value_counts().sort_index().items()
            },
        },
        "geographic_summary": {
            "rows_with_both_coordinates": int(both_present.sum()),
            "valid_coordinate_rows": int(valid_coordinates.sum()),
            "invalid_coordinate_rows_with_both_values": int(
                (both_present & ~valid_coordinates).sum()
            ),
            "missing_latitude_count": int(lat.isna().sum()),
            "missing_longitude_count": int(lon.isna().sum()),
            "unique_valid_coordinate_pairs": int(
                pd.DataFrame({
                    "latitude": lat[valid_coordinates],
                    "longitude": lon[valid_coordinates],
                }).drop_duplicates().shape[0]
            ),
        },
        "field_profiles": {
            column: field_profile(df, column) for column in df.columns
        },
        "notes": [
            "Profile describes the existing canonical CSV only.",
            "A date column alone does not establish time-series readiness.",
            "Profile statistics do not independently prove real-world accuracy.",
            "Synthetic records must not be represented as real-world observations.",
        ],
    }

    OUTPUT_FILE.write_text(
        json.dumps(json_safe(profile), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("=" * 60)
    print("INFOCREON PHASE 3 — CANONICAL DATA PROFILE")
    print("=" * 60)
    print(f"Rows: {profile['row_count']}")
    print(f"Columns: {profile['column_count']}")
    print(f"File size: {profile['file_size_mb']} MB")
    print(f"Unique timestamps: {profile['date_summary']['unique_timestamps']}")
    print(f"Unique calendar dates: {profile['date_summary']['unique_calendar_dates']}")
    print(f"Valid coordinate rows: {profile['geographic_summary']['valid_coordinate_rows']}")
    print(f"Missing expected columns: {missing_columns}")
    print(f"Profile saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()