
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "canonical" / "intelligence_data.csv"
OUTPUT_FILE = (
    ROOT / "data-science" / "outputs" / "representativeness_assessment.json"
)


def distribution(series):
    counts = series.fillna("<NULL>").astype(str).value_counts(dropna=False)
    return {str(key): int(value) for key, value in counts.items()}


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Canonical dataset not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE, low_memory=False)
    dates = pd.to_datetime(df["observed_at"], errors="coerce", utc=True)

    cities = df["entity_name"].fillna("<NULL>").astype(str).str.strip()
    pollutants = df["subcategory"].fillna("<NULL>").astype(str).str.strip().str.lower()
    timestamps = dates.dt.strftime("%Y-%m-%dT%H:%M:%SZ").fillna("<INVALID>")

    city_counts = distribution(cities)
    pollutant_counts = distribution(pollutants)
    timestamp_counts = distribution(timestamps)

    city_pollutant = pd.DataFrame({
        "city": cities,
        "pollutant": pollutants,
    }).value_counts().rename("records").reset_index()

    city_pollutant_timestamp = pd.DataFrame({
        "city": cities,
        "pollutant": pollutants,
        "timestamp": timestamps,
    }).value_counts().rename("records").reset_index()

    expected_cities = 8
    expected_pollutants = 4
    expected_timestamps_per_group = 3

    actual_cities = int(cities[cities != "<NULL>"].nunique())
    actual_pollutants = int(pollutants[pollutants != "<NULL>"].nunique())
    actual_timestamps = int(dates.nunique(dropna=True))

    # These are structural coverage checks, not evidence of population-level
    # representativeness or real-world sampling quality.
    per_city_pollutant_counts = city_pollutant["records"].tolist()
    city_pollutant_balanced = (
        bool(per_city_pollutant_counts)
        and len(set(per_city_pollutant_counts)) == 1
    )

    timestamp_counts_per_group = city_pollutant_timestamp.groupby(
        ["city", "pollutant"]
    )["timestamp"].nunique()

    groups_with_expected_timestamp_count = int(
        (timestamp_counts_per_group == expected_timestamps_per_group).sum()
    )

    expected_group_count = expected_cities * expected_pollutants

    result = {
        "assessment_name": "Canonical Dataset Representativeness Assessment",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": "data/canonical/intelligence_data.csv",
        "row_count": int(len(df)),
        "expected_design": {
            "cities": expected_cities,
            "pollutants": expected_pollutants,
            "timestamps_per_city_pollutant": expected_timestamps_per_group,
            "expected_canonical_records": (
                expected_cities
                * expected_pollutants
                * expected_timestamps_per_group
            ),
        },
        "observed_coverage": {
            "unique_city_names": actual_cities,
            "city_distribution": city_counts,
            "unique_pollutant_subcategories": actual_pollutants,
            "pollutant_distribution": pollutant_counts,
            "unique_timestamps": actual_timestamps,
            "unique_calendar_dates": int(
                dates.dropna().dt.strftime("%Y-%m-%d").nunique()
            ),
            "timestamp_distribution": timestamp_counts,
            "city_pollutant_record_counts": city_pollutant.to_dict(
                orient="records"
            ),
            "city_pollutant_timestamp_counts": city_pollutant_timestamp.to_dict(
                orient="records"
            ),
        },
        "structural_checks": {
            "row_count_matches_expected_design": (
                len(df) == expected_cities
                * expected_pollutants
                * expected_timestamps_per_group
            ),
            "city_count_matches_expected": actual_cities == expected_cities,
            "pollutant_count_matches_expected": (
                actual_pollutants == expected_pollutants
            ),
            "city_pollutant_groups_balanced": city_pollutant_balanced,
            "groups_with_expected_timestamp_count": (
                groups_with_expected_timestamp_count
            ),
            "expected_city_pollutant_groups": expected_group_count,
            "all_groups_have_expected_timestamp_count": (
                groups_with_expected_timestamp_count == expected_group_count
            ),
        },
        "limitations": [
            "The dataset is controlled synthetic data, not a probability sample of real-world air quality.",
            "Balanced counts do not establish geographic, demographic, seasonal, or environmental representativeness.",
            "Only a single calendar date was observed in the initial profile; long-term temporal coverage is limited.",
            "City names and pollutant coverage are assessed from the canonical file, not external verification.",
        ],
        "interpretation": (
            "Use the structural checks to verify the intended dataset design. "
            "Do not claim real-world representativeness from balance alone."
        ),
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print("=" * 60)
    print("INFOCREON PHASE 3 — REPRESENTATIVENESS ASSESSMENT")
    print("=" * 60)
    print(f"Rows: {len(df)}")
    print(f"Unique cities: {actual_cities}")
    print(f"Unique pollutants: {actual_pollutants}")
    print(f"Unique timestamps: {actual_timestamps}")
    print(f"City-pollutant groups with expected timestamps: "
          f"{groups_with_expected_timestamp_count}/{expected_group_count}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()