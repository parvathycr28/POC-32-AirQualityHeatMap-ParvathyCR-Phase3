from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data" / "source-sample" / "source_sample.csv"
OUTPUT_FILE = ROOT / "data" / "canonical" / "intelligence_data.csv"

DATA_VERSION = "phase3-v1.0"


CANONICAL_COLUMNS = [
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


def clean_entity_id(value):
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Source sample not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    required_source_columns = [
        "city",
        "country",
        "pollutant",
        "value",
        "unit",
        "timestamp",
        "population",
        "exposure_score",
        "regional_average",
        "percentage_above_regional_average",
        "source",
        "latitude",
        "longitude",
    ]

    missing = [
        column
        for column in required_source_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Source sample is missing columns: {missing}"
        )

    canonical = pd.DataFrame()

    canonical["record_id"] = [
        f"aq-{index:04d}"
        for index in range(1, len(df) + 1)
    ]

    canonical["record_type"] = "measurement"

    canonical["observed_at"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
        utc=True,
    )

    canonical["entity_id"] = df["city"].map(clean_entity_id)

    canonical["related_entity_id"] = ""

    canonical["entity_name"] = df["city"].astype(str).str.strip()

    canonical["category"] = "air_quality"

    canonical["subcategory"] = (
        df["pollutant"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    canonical["status"] = "observed"

    canonical["stage"] = "observation"

    canonical["metric_name"] = (
        df["pollutant"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    canonical["metric_value"] = pd.to_numeric(
        df["value"],
        errors="coerce",
    )

    canonical["metric_unit"] = (
        df["unit"]
        .astype(str)
        .str.strip()
    )

    canonical["text_value"] = (
        df["country"]
        .astype(str)
        .str.strip()
    )

    canonical["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce",
    )

    canonical["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce",
    )

    canonical["source_name"] = (
        df["source"]
        .astype(str)
        .str.strip()
    )

    canonical["source_record_id"] = [
        (
            f"{clean_entity_id(row.city)}-"
            f"{str(row.pollutant).strip().lower()}-"
            f"{index:04d}"
        )
        for index, row in df.iterrows()
    ]

    # The current Phase 3 source is the application's fallback/mock data.
    canonical["is_synthetic"] = "true"

    canonical["data_version"] = DATA_VERSION

    canonical["observed_at"] = canonical["observed_at"].dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    canonical = canonical[CANONICAL_COLUMNS]

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    canonical.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    print("Canonical standardization completed.")
    print(f"Input rows: {len(df)}")
    print(f"Output rows: {len(canonical)}")
    print(f"Output columns: {len(canonical.columns)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
