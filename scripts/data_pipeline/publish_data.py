from pathlib import Path
import hashlib
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

CANONICAL = (
    ROOT
    / "data"
    / "canonical"
    / "intelligence_data.csv"
)

OUTPUT = (
    ROOT
    / "data"
    / "published"
    / "intelligence_data.json"
)

DATA_VERSION = "phase3-v1.1"


def sha256_file(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def clean_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        value = value.item()

    return value


def main():
    if not CANONICAL.exists():
        raise FileNotFoundError(
            f"Canonical dataset not found: {CANONICAL}"
        )

    df = pd.read_csv(CANONICAL)

    canonical_hash = sha256_file(CANONICAL)

    records = []

    for record in df.to_dict(orient="records"):
        cleaned_record = {
            key: clean_value(value)
            for key, value in record.items()
        }

        records.append(cleaned_record)

    payload = {
        "dataset": (
            "Infocreon Aether Pulse "
            "Canonical Intelligence Dataset"
        ),
        "data_version": DATA_VERSION,
        "record_count": len(records),
        "column_count": len(df.columns),
        "source": (
            "data/canonical/intelligence_data.csv"
        ),
        "canonical_sha256": canonical_hash,
        "records": records,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ),
        encoding="utf-8",
    )

    print("Published JSON generation completed.")
    print(f"Input rows: {len(df)}")
    print(f"Input columns: {len(df.columns)}")
    print(f"Canonical SHA256: {canonical_hash}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()