from pathlib import Path
import json
import csv


ROOT_DIR = Path(__file__).resolve().parents[2]

SOURCE_JSON = (
    ROOT_DIR
    / "data"
    / "source-sample"
    / "source_sample.json"
)

OUTPUT_CSV = (
    ROOT_DIR
    / "data"
    / "source-sample"
    / "source_sample.csv"
)


def extract_features():
    with SOURCE_JSON.open("r", encoding="utf-8") as file:
        data = json.load(file)

    features = data.get("features", [])

    rows = []

    for feature in features:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [])

        longitude = coordinates[0] if len(coordinates) > 0 else None
        latitude = coordinates[1] if len(coordinates) > 1 else None

        row = {
            "city": properties.get("city"),
            "country": properties.get("country"),
            "pollutant": properties.get("pollutant"),
            "value": properties.get("value"),
            "unit": properties.get("unit"),
            "timestamp": properties.get("timestamp"),
            "population": properties.get("population"),
            "exposure_score": properties.get("exposure_score"),
            "regional_average": properties.get("regional_average"),
            "percentage_above_regional_average": properties.get(
                "percentage_above_regional_average"
            ),
            "source": properties.get("source"),
            "latitude": latitude,
            "longitude": longitude,
        }

        rows.append(row)

    return rows


def main():
    rows = extract_features()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
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

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"Extracted {len(rows)} records")
    print(f"Created: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
