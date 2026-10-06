from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT / "data" / "source-sample" / "source_sample.csv"
OUTPUT_FILE = ROOT / "data" / "source-sample" / "source_sample.csv"

RANDOM_SEED = 42
MAX_ROWS = 10_000


def main():
    df = pd.read_csv(INPUT_FILE)

    if len(df) <= MAX_ROWS:
        sampled = df.copy()
        method = "Full source retained because source row count is below canonical limit."
    else:
        # Coverage-aware sampling:
        # preserve one representative record per city and pollutant first.
        grouped = (
            df.groupby(["city", "pollutant"], dropna=False)
            .sample(n=1, random_state=RANDOM_SEED)
        )

        remaining = df.drop(grouped.index)

        remaining_count = MAX_ROWS - len(grouped)

        if remaining_count > 0 and not remaining.empty:
            additional = remaining.sample(
                n=min(remaining_count, len(remaining)),
                random_state=RANDOM_SEED,
            )
            sampled = pd.concat([grouped, additional])
        else:
            sampled = grouped

        method = (
            "Coverage-aware sampling by city and pollutant "
            f"with random seed {RANDOM_SEED}."
        )

    sampled.to_csv(OUTPUT_FILE, index=False)

    print(f"Sampling method: {method}")
    print(f"Input rows: {len(df)}")
    print(f"Output rows: {len(sampled)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
