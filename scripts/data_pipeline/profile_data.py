from pathlib import Path
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

CANONICAL = ROOT / "data" / "canonical" / "intelligence_data.csv"
MANIFEST = ROOT / "data" / "manifest.json"
PROFILE = ROOT / "data" / "quality" / "data_profile.json"


def main():
    df = pd.read_csv(CANONICAL)

    with open(MANIFEST, "r", encoding="utf-8") as file:
        manifest = json.load(file)

    profile = {
        "dataset": "Infocreon Aether Pulse Canonical Intelligence Dataset",
        "data_version": manifest.get("dataset_version"),
        "source_name": sorted(
            df["source_name"].dropna().astype(str).unique().tolist()
        ),
        "record_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": {},
        "null_counts": {},
        "unique_counts": {},
    }

    for column in df.columns:
        series = df[column]

        profile["columns"][column] = {
            "dtype": str(series.dtype),
            "non_null_count": int(series.notna().sum()),
            "null_count": int(series.isna().sum()),
            "unique_count": int(series.nunique(dropna=True)),
        }

        profile["null_counts"][column] = int(series.isna().sum())
        profile["unique_counts"][column] = int(
            series.nunique(dropna=True)
        )

    numeric_columns = [
        "metric_value",
        "latitude",
        "longitude",
    ]

    profile["numeric_summary"] = {}

    for column in numeric_columns:
        values = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        profile["numeric_summary"][column] = {
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
            "median": float(values.median()),
        }

    profile["coverage"] = {
        "entities": sorted(
            df["entity_name"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        ),
        "categories": sorted(
            df["category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        ),
        "subcategories": sorted(
            df["subcategory"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        ),
        "record_types": sorted(
            df["record_type"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        ),
    }

    profile["synthetic_status"] = {
        "is_synthetic_values": sorted(
            df["is_synthetic"]
            .astype(str)
            .str.lower()
            .unique()
            .tolist()
        ),
        "all_records_synthetic": bool(
            df["is_synthetic"]
            .astype(str)
            .str.lower()
            .eq("true")
            .all()
        ),
    }

    PROFILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    PROFILE.write_text(
        json.dumps(
            profile,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Data profile generation completed.")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Output: {PROFILE}")


if __name__ == "__main__":
    main()
