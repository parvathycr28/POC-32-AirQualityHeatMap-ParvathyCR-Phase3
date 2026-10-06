from pathlib import Path
import hashlib
import json
import math
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"

CANONICAL = (
    DATA_DIR
    / "canonical"
    / "intelligence_data.csv"
)

PUBLISHED = (
    DATA_DIR
    / "published"
    / "intelligence_data.json"
)

MANIFEST = DATA_DIR / "manifest.json"
SCHEMA = DATA_DIR / "schema.json"

REPORT = (
    DATA_DIR
    / "quality"
    / "validation_report.json"
)

MAX_DATA_MB = 10
MAX_FILE_MB = 5
MAX_ROWS = 10_000
MAX_COLS = 50

EXPECTED_VERSION = "phase3-v1.1"

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


def sha256_file(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def reject_json_constants(value):
    raise ValueError(
        f"Invalid JSON constant detected: {value}"
    )


def clean_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        value = value.item()

    return value


def canonical_records(df):
    return [
        {
            key: clean_value(value)
            for key, value in row.items()
        }
        for row in df.to_dict(
            orient="records"
        )
    ]


def main():
    errors = []
    checks = []

    required_paths = [
        DATA_DIR / "README.md",
        MANIFEST,
        SCHEMA,
        DATA_DIR / "source-sample" / "source_sample.csv",
        CANONICAL,
        PUBLISHED,
        DATA_DIR / "quality" / "sampling_report.md",
    ]

    for path in required_paths:
        if path.exists():
            checks.append(
                f"Present: {path.relative_to(ROOT)}"
            )
        else:
            add_error(
                errors,
                f"Missing required path: "
                f"{path.relative_to(ROOT)}",
            )

    total_bytes = 0

    if DATA_DIR.exists():
        total_bytes = sum(
            path.stat().st_size
            for path in DATA_DIR.rglob("*")
            if path.is_file()
        )

    total_mb = total_bytes / 1024 / 1024

    checks.append(
        f"Total /data size: {total_mb:.3f} MB"
    )

    if total_mb > MAX_DATA_MB:
        add_error(
            errors,
            f"Total /data size exceeds {MAX_DATA_MB} MB",
        )

    df = None

    if CANONICAL.exists():
        canonical_mb = (
            CANONICAL.stat().st_size
            / 1024
            / 1024
        )

        checks.append(
            f"Canonical CSV size: "
            f"{canonical_mb:.3f} MB"
        )

        if canonical_mb > MAX_FILE_MB:
            add_error(
                errors,
                f"Canonical CSV exceeds "
                f"{MAX_FILE_MB} MB",
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

        checks.append(
            f"Canonical rows: {row_count}"
        )

        checks.append(
            f"Canonical columns: {column_count}"
        )

        if row_count > MAX_ROWS:
            add_error(
                errors,
                f"Canonical row count exceeds "
                f"{MAX_ROWS}",
            )

        if column_count > MAX_COLS:
            add_error(
                errors,
                f"Canonical column count exceeds "
                f"{MAX_COLS}",
            )

        if list(df.columns) != MANDATORY_COLUMNS:
            add_error(
                errors,
                "Canonical columns do not exactly "
                "match required order",
            )
        else:
            checks.append(
                "Canonical column order: PASS"
            )

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
        else:
            checks.append(
                "record_id uniqueness: PASS"
            )

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

        if set(
            df["data_version"]
            .astype(str)
        ) != {EXPECTED_VERSION}:
            add_error(
                errors,
                "Canonical data_version is incorrect",
            )
        else:
            checks.append(
                "Canonical data version: PASS"
            )

        parsed_dates = pd.to_datetime(
            df["observed_at"],
            errors="coerce",
            utc=True,
        )

        if parsed_dates.isna().any():
            add_error(
                errors,
                "observed_at contains "
                "unparseable dates",
            )
        else:
            checks.append(
                "Date parsing: PASS"
            )

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
                    f"{column} contains "
                    f"non-numeric values",
                )

        latitude = pd.to_numeric(
            df["latitude"],
            errors="coerce",
        )

        longitude = pd.to_numeric(
            df["longitude"],
            errors="coerce",
        )

        metric_values = pd.to_numeric(
            df["metric_value"],
            errors="coerce",
        )

        if (
            (latitude < -90)
            | (latitude > 90)
        ).any():
            add_error(
                errors,
                "latitude contains values outside "
                "[-90, 90]",
            )

        if (
            (longitude < -180)
            | (longitude > 180)
        ).any():
            add_error(
                errors,
                "longitude contains values outside "
                "[-180, 180]",
            )

        if (metric_values < 0).any():
            add_error(
                errors,
                "metric_value contains negative values",
            )

        checks.append(
            "Numeric field and range validation: PASS"
        )

        valid_boolean_values = {
            "true",
            "false",
        }

        boolean_values = (
            df["is_synthetic"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        if not boolean_values.isin(
            valid_boolean_values
        ).all():
            add_error(
                errors,
                "is_synthetic must contain "
                "only true or false",
            )
        else:
            checks.append(
                "Boolean validation: PASS"
            )

        allowed_pollutants = {
            "pm2.5",
            "pm10",
            "no2",
            "o3",
        }

        if not df["subcategory"].isin(
            allowed_pollutants
        ).all():
            add_error(
                errors,
                "subcategory contains "
                "unsupported pollutant values",
            )

        if not df["metric_name"].isin(
            allowed_pollutants
        ).all():
            add_error(
                errors,
                "metric_name contains "
                "unsupported pollutant values",
            )

        checks.append(
            "Allowed pollutant values: PASS"
        )

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

        if manifest_version != EXPECTED_VERSION:
            add_error(
                errors,
                "Manifest dataset version is incorrect",
            )
        else:
            checks.append(
                "Manifest version: PASS"
            )

        expected_records = (
            manifest_data
            .get("canonical", {})
            .get("records")
        )

        if expected_records != len(df):
            add_error(
                errors,
                "Manifest record count does not "
                "match canonical CSV",
            )
        else:
            checks.append(
                "Manifest record count: PASS"
            )

        expected_columns = (
            manifest_data
            .get("canonical", {})
            .get("columns")
        )

        if expected_columns != len(df.columns):
            add_error(
                errors,
                "Manifest column count does not "
                "match canonical CSV",
            )
        else:
            checks.append(
                "Manifest column count: PASS"
            )

    published_data = None

    if PUBLISHED.exists():

        try:
            with open(
                PUBLISHED,
                "r",
                encoding="utf-8",
            ) as file:
                published_data = json.load(
                    file,
                    parse_constant=reject_json_constants,
                )

            checks.append(
                "Published JSON syntax: PASS"
            )

        except Exception as error:
            add_error(
                errors,
                f"Published JSON is invalid: {error}",
            )

    if published_data is not None and df is not None:

        if not isinstance(
            published_data.get("records"),
            list,
        ):
            add_error(
                errors,
                "Published JSON records is not a list",
            )
        else:
            published_records = (
                published_data["records"]
            )

            if len(published_records) != len(df):
                add_error(
                    errors,
                    "Published JSON record count does "
                    "not match canonical CSV",
                )
            else:
                checks.append(
                    "Published record count: PASS"
                )

            if (
                published_data.get("column_count")
                != len(df.columns)
            ):
                add_error(
                    errors,
                    "Published JSON column count does "
                    "not match canonical CSV",
                )
            else:
                checks.append(
                    "Published column count: PASS"
                )

            if (
                published_data.get("data_version")
                != EXPECTED_VERSION
            ):
                add_error(
                    errors,
                    "Published JSON data version "
                    "is stale or incorrect",
                )
            else:
                checks.append(
                    "Published data version: PASS"
                )

            canonical_hash = sha256_file(
                CANONICAL
            )

            published_hash = (
                published_data.get(
                    "canonical_sha256"
                )
            )

            if published_hash != canonical_hash:
                add_error(
                    errors,
                    "Published JSON is stale: "
                    "canonical_sha256 does not "
                    "match current canonical CSV",
                )
            else:
                checks.append(
                    "Published/current canonical "
                    "hash: PASS"
                )

            expected_records = canonical_records(
                df
            )

            if published_records != expected_records:
                add_error(
                    errors,
                    "Published JSON records do not "
                    "match the current canonical CSV",
                )
            else:
                checks.append(
                    "Published/canonical record "
                    "content: PASS"
                )

    status = (
        "PASS"
        if not errors
        else "FAIL"
    )

    result = {
        "status": status,
        "dataset": (
            "Infocreon Aether Pulse "
            "Canonical Intelligence Dataset"
        ),
        "data_version": EXPECTED_VERSION,
        "canonical_file": str(
            CANONICAL.relative_to(ROOT)
        ),
        "published_file": str(
            PUBLISHED.relative_to(ROOT)
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
        "published_json_valid": (
            published_data is not None
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
    print(
        "INFOCREON PHASE 3 — "
        "CANONICAL DATA VALIDATION"
    )
    print("=" * 60)
    print(f"Status: {status}")
    print(
        f"Rows: {result['canonical_rows']}"
    )
    print(
        f"Columns: {result['canonical_columns']}"
    )
    print(
        f"Data size: {total_mb:.3f} MB"
    )
    print(f"Report: {REPORT}")

    if errors:
        print("\nVALIDATION ERRORS:")

        for error in errors:
            print(f"- {error}")

        sys.exit(1)

    print(
        "\nCanonical data validation passed."
    )


if __name__ == "__main__":
    main()