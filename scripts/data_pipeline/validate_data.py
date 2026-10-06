from pathlib import Path
import json
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"
CANONICAL = DATA_DIR / "canonical" / "intelligence_data.csv"
MANIFEST = DATA_DIR / "manifest.json"
SCHEMA = DATA_DIR / "schema.json"
REPORT = DATA_DIR / "quality" / "validation_report.json"

MAX_DATA_MB = 10
MAX_FILE_MB = 5
MAX_ROWS = 10_000
MAX_COLS = 50

MANDATORY_COLUMNS = [
    "record_id",
    "record_type",
    "observed_at",
    "entity_id",
    "related_entity_id",
    "entity_name",
    "category",
    "subcategory",
    "status",
    "stage",
    "metric_name",
    "metric_value",
    "metric_unit",
    "text_value",
    "latitude",
    "longitude",
    "source_name",
    "source_record_id",
    "is_synthetic",
    "data_version",
]


def add_error(errors, message):
    errors.append(message)


def main():
    errors = []
    checks = []

    required_paths = [
        DATA_DIR / "README.md",
        MANIFEST,
        SCHEMA,
        DATA_DIR / "source-sample" / "source_sample.csv",
        CANONICAL,
    ]

    for path in required_paths:
        if path.exists():
            checks.append(f"Present: {path.relative_to(ROOT)}")
        else:
            add_error(
                errors,
                f"Missing required path: {path.relative_to(ROOT)}",
            )

    total_bytes = 0

    if DATA_DIR.exists():
        total_bytes = sum(
            path.stat().st_size
            for path in DATA_DIR.rglob("*")
            if path.is_file()
        )

    total_mb = total_bytes / 1024 / 1024

    if total_mb > MAX_DATA_MB:
        add_error(
            errors,
            f"Total /data size exceeds {MAX_DATA_MB} MB",
        )

    checks.append(
        f"Total /data size: {total_mb:.3f} MB"
    )

    df = None

    if CANONICAL.exists():
        canonical_mb = CANONICAL.stat().st_size / 1024 / 1024

        checks.append(
            f"Canonical CSV size: {canonical_mb:.3f} MB"
        )

        if canonical_mb > MAX_FILE_MB:
            add_error(
                errors,
                f"Canonical CSV exceeds {MAX_FILE_MB} MB",
            )

        try:
            df = pd.read_csv(CANONICAL)
        except Exception as error:
            add_error(
                errors,
                f"Unable to read canonical CSV: {error}",
            )

    if df is not None:
        row_count = len(df)
        column_count = len(df.columns)

        checks.append(f"Canonical rows: {row_count}")
        checks.append(f"Canonical columns: {column_count}")

        if row_count > MAX_ROWS:
            add_error(
                errors,
                f"Canonical row count exceeds {MAX_ROWS}",
            )

        if column_count > MAX_COLS:
            add_error(
                errors,
                f"Canonical column count exceeds {MAX_COLS}",
            )

        if list(df.columns) != MANDATORY_COLUMNS:
            add_error(
                errors,
                "Canonical columns do not exactly match the required order",
            )
        else:
            checks.append("Canonical column order: PASS")

        if df["record_id"].isna().any():
            add_error(
                errors,
                "record_id contains null values",
            )

        if df["record_id"].duplicated().any():
            add_error(
                errors,
                "record_id contains duplicate values",
            )

        checks.append("record_id uniqueness: PASS")

        for required in [
            "record_type",
            "source_name",
            "is_synthetic",
            "data_version",
        ]:
            if df[required].isna().any():
                add_error(
                    errors,
                    f"{required} contains missing values",
                )

        checks.append("Required metadata fields: PASS")

        parsed_dates = pd.to_datetime(
            df["observed_at"],
            errors="coerce",
            utc=True,
        )

        if parsed_dates.isna().any():
            add_error(
                errors,
                "observed_at contains unparseable dates",
            )
        else:
            checks.append("Date parsing: PASS")

        numeric_columns = [
            "metric_value",
            "latitude",
            "longitude",
        ]

        for column in numeric_columns:
            numeric_values = pd.to_numeric(
                df[column],
                errors="coerce",
            )

            invalid = (
                numeric_values.isna()
                & df[column].notna()
            )

            if invalid.any():
                add_error(
                    errors,
                    f"{column} contains non-numeric values",
                )

        checks.append("Numeric field validation: PASS")

        valid_boolean_values = {"true", "false"}

        boolean_values = (
            df["is_synthetic"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        invalid_boolean = ~boolean_values.isin(
            valid_boolean_values
        )

        if invalid_boolean.any():
            add_error(
                errors,
                "is_synthetic must contain only true or false",
            )
        else:
            checks.append("Boolean validation: PASS")

    manifest_data = None

    if MANIFEST.exists():
        try:
            with open(
                MANIFEST,
                "r",
                encoding="utf-8",
            ) as file:
                manifest_data = json.load(file)
        except Exception as error:
            add_error(
                errors,
                f"Unable to read manifest.json: {error}",
            )

    if manifest_data and df is not None:
        manifest_version = manifest_data.get(
            "dataset_version"
        )

        actual_versions = set(
            df["data_version"]
            .dropna()
            .astype(str)
        )

        if actual_versions != {manifest_version}:
            add_error(
                errors,
                (
                    "Manifest dataset_version does not "
                    "match canonical data_version"
                ),
            )
        else:
            checks.append("Manifest/data version consistency: PASS")

        expected_records = (
            manifest_data
            .get("canonical", {})
            .get("records")
        )

        if expected_records != len(df):
            add_error(
                errors,
                "Manifest canonical record count does not match CSV",
            )
        else:
            checks.append(
                "Manifest record count consistency: PASS"
            )

        expected_columns = (
            manifest_data
            .get("canonical", {})
            .get("columns")
        )

        if expected_columns != len(df.columns):
            add_error(
                errors,
                "Manifest canonical column count does not match CSV",
            )
        else:
            checks.append(
                "Manifest column count consistency: PASS"
            )

    status = "PASS" if not errors else "FAIL"

    result = {
        "status": status,
        "dataset": "Infocreon Aether Pulse Canonical Intelligence Dataset",
        "data_version": (
            manifest_data.get("dataset_version")
            if manifest_data
            else None
        ),
        "canonical_file": str(
            CANONICAL.relative_to(ROOT)
        ),
        "canonical_rows": (
            len(df)
            if df is not None
            else None
        ),
        "canonical_columns": (
            len(df.columns)
            if df is not None
            else None
        ),
        "total_data_size_mb": round(
            total_mb,
            3,
        ),
        "checks": checks,
        "errors": errors,
    }

    REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 60)
    print("INFOCREON PHASE 3 — CANONICAL DATA VALIDATION")
    print("=" * 60)
    print(f"Status: {status}")
    print(f"Rows: {result['canonical_rows']}")
    print(f"Columns: {result['canonical_columns']}")
    print(f"Data size: {total_mb:.3f} MB")
    print(f"Report: {REPORT}")

    if errors:
        print("\nVALIDATION ERRORS:")
        for error in errors:
            print(f"- {error}")

        sys.exit(1)

    print("\nCanonical data validation passed.")


if __name__ == "__main__":
    main()
