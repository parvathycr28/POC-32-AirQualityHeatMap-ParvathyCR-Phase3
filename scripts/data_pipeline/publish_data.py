from pathlib import Path
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

CANONICAL = ROOT / "data" / "canonical" / "intelligence_data.csv"
OUTPUT = ROOT / "data" / "published" / "intelligence_data.json"


def main():
    if not CANONICAL.exists():
        raise FileNotFoundError(
            f"Canonical dataset not found: {CANONICAL}"
        )

    df = pd.read_csv(CANONICAL)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    records = df.where(
        pd.notna(df),
        None,
    ).to_dict(orient="records")

    payload = {
        "dataset": "Infocreon Aether Pulse Canonical Intelligence Dataset",
        "data_version": "phase3-v1.0",
        "record_count": len(records),
        "column_count": len(df.columns),
        "source": "data/canonical/intelligence_data.csv",
        "records": records,
    }

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("Published JSON generation completed.")
    print(f"Input rows: {len(df)}")
    print(f"Input columns: {len(df.columns)}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
