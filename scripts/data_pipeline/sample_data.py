from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "source-sample"
    / "source_sample_full.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "source-sample"
    / "source_sample.csv"
)

RANDOM_SEED = 42
TIME_POINTS_PER_GROUP = 3


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Full source dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "city",
        "pollutant",
        "timestamp",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    sampled = (
        df.sort_values(
            ["city", "pollutant", "timestamp"]
        )
        .groupby(
            ["city", "pollutant"],
            group_keys=False,
        )
        .apply(
            lambda group: group.sample(
                n=min(
                    TIME_POINTS_PER_GROUP,
                    len(group),
                ),
                random_state=RANDOM_SEED,
            )
        )
        .reset_index(drop=True)
    )

    sampled = sampled.sort_values(
        ["city", "pollutant", "timestamp"]
    ).reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sampled.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    print("Coverage-aware sampling completed.")
    print(f"Input rows: {len(df)}")
    print(f"Output rows: {len(sampled)}")
    print(f"Cities: {sampled['city'].nunique()}")
    print(f"Pollutants: {sampled['pollutant'].nunique()}")
    print(
        f"Time points per city/pollutant: "
        f"{TIME_POINTS_PER_GROUP}"
    )
    print(f"Random seed: {RANDOM_SEED}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()