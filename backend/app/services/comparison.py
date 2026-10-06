import pandas as pd


def compare_cities(features: list[dict]) -> list[dict]:
    rows = []

    for feature in features:
        properties = feature["properties"]

        rows.append({
            "city": properties["city"],
            "pollutant": properties["pollutant"],
            "value": properties["value"],
            "population": properties.get("population"),
            "exposure_score": properties.get("exposure_score"),
            "percentage_above_regional_average": properties.get(
                "percentage_above_regional_average"
            ),
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return []

    return df.sort_values(
        by="exposure_score",
        ascending=False,
    ).to_dict(orient="records")