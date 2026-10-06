from pathlib import Path
import csv
from datetime import datetime, timedelta, timezone


ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    ROOT
    / "data"
    / "source-sample"
    / "source_sample_full.csv"
)

CITIES = [
    {
        "city": "Delhi",
        "country": "India",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "population": 32900000,
    },
    {
        "city": "Mumbai",
        "country": "India",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "population": 21600000,
    },
    {
        "city": "Bengaluru",
        "country": "India",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "population": 14000000,
    },
    {
        "city": "Kolkata",
        "country": "India",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "population": 15100000,
    },
    {
        "city": "Chennai",
        "country": "India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "population": 11500000,
    },
    {
        "city": "Hyderabad",
        "country": "India",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "population": 10500000,
    },
    {
        "city": "Pune",
        "country": "India",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "population": 7400000,
    },
    {
        "city": "Ahmedabad",
        "country": "India",
        "latitude": 23.0225,
        "longitude": 72.5714,
        "population": 8500000,
    },
]


POLLUTANTS = {
    "PM2.5": {
        "unit": "µg/m³",
        "base": 42.0,
    },
    "PM10": {
        "unit": "µg/m³",
        "base": 76.0,
    },
    "NO2": {
        "unit": "µg/m³",
        "base": 34.0,
    },
    "O3": {
        "unit": "µg/m³",
        "base": 58.0,
    },
}


TIMESTAMPS = [
    datetime(2026, 8, 23, 0, 0, tzinfo=timezone.utc),
    datetime(2026, 8, 23, 4, 0, tzinfo=timezone.utc),
    datetime(2026, 8, 23, 8, 0, tzinfo=timezone.utc),
    datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc),
    datetime(2026, 8, 23, 16, 0, tzinfo=timezone.utc),
    datetime(2026, 8, 23, 20, 0, tzinfo=timezone.utc),
]


CITY_FACTORS = {
    "Delhi": 1.55,
    "Mumbai": 1.10,
    "Bengaluru": 0.78,
    "Kolkata": 1.20,
    "Chennai": 0.92,
    "Hyderabad": 1.00,
    "Pune": 0.88,
    "Ahmedabad": 1.18,
}


def calculate_value(city_factor, pollutant_base, city_index, time_index):
    variation = (
        ((city_index * 7) + (time_index * 5)) % 13
    ) - 6

    time_factor = (
        1.0
        + (0.08 if time_index in (1, 2) else 0)
        - (0.05 if time_index in (4, 5) else 0)
    )

    value = (
        pollutant_base
        * city_factor
        * time_factor
        + variation
    )

    return round(max(value, 1.0), 2)


def main():
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows = []

    record_number = 1

    for city_index, city in enumerate(CITIES):
        for pollutant, config in POLLUTANTS.items():
            for time_index, timestamp in enumerate(TIMESTAMPS):

                value = calculate_value(
                    CITY_FACTORS[city["city"]],
                    config["base"],
                    city_index,
                    time_index,
                )

                regional_average = round(
                    config["base"] * 1.05,
                    2,
                )

                exposure_score = round(
                    min(100, value / regional_average * 70),
                    1,
                )

                percentage_above_average = round(
                    (
                        (value - regional_average)
                        / regional_average
                    )
                    * 100,
                    2,
                )

                rows.append(
                    {
                        "city": city["city"],
                        "country": city["country"],
                        "pollutant": pollutant,
                        "value": value,
                        "unit": config["unit"],
                        "timestamp": timestamp.strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "population": city["population"],
                        "exposure_score": exposure_score,
                        "regional_average": regional_average,
                        "percentage_above_regional_average":
                            percentage_above_average,
                        "source":
                            "Synthetic OpenAQ-shaped sample",
                        "latitude": city["latitude"],
                        "longitude": city["longitude"],
                    }
                )

                record_number += 1

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

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    print("Controlled source dataset generated.")
    print(f"Cities: {len(CITIES)}")
    print(f"Pollutants: {len(POLLUTANTS)}")
    print(f"Time points: {len(TIMESTAMPS)}")
    print(f"Records: {len(rows)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()