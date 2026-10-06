from datetime import datetime, timezone

from app.adapters.openaq import OpenAQAdapter
from app.services.exposure import (
    calculate_exposure_score,
    percentage_above_average,
)
from app.utils.fallback import load_fallback_data


PARAMETERS = {
    "pm25": 2,
    "pm10": 1,
    "o3": 3,
    "no2": 5,
}


class AirQualityService:
    def __init__(self):
        self.openaq = OpenAQAdapter()

    def get_map_data(
        self,
        pollutant: str = "pm25",
    ) -> dict:

        parameter_id = PARAMETERS.get(
            pollutant.lower(),
            PARAMETERS["pm25"],
        )

        try:
            raw = self.openaq.get_latest(
                parameter_id=parameter_id,
                limit=100,
            )

            features = []

            values = [
                item.get("value")
                for item in raw.get("results", [])
                if item.get("value") is not None
            ]

            regional_average = (
                sum(values) / len(values)
                if values
                else 0
            )

            for item in raw.get("results", []):

                coordinates = item.get("coordinates")

                if not coordinates:
                    continue

                value = item.get("value")

                if value is None:
                    continue

                location = item.get("locationsId")

                city = (
                    item.get("locality")
                    or item.get("location")
                    or f"Station {location}"
                )

                feature = {
                    "type": "Feature",
                    "properties": {
                        "city": city,
                        "country": None,
                        "pollutant": pollutant.upper(),
                        "value": float(value),
                        "unit": item.get("unit", "µg/m³"),
                        "timestamp": self._timestamp(item),
                        "population": None,
                        "exposure_score": calculate_exposure_score(
                            float(value)
                        ),
                        "regional_average": round(
                            regional_average,
                            2,
                        ),
                        "percentage_above_regional_average":
                            percentage_above_average(
                                float(value),
                                regional_average,
                            ),
                        "source": "OpenAQ",
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            coordinates["longitude"],
                            coordinates["latitude"],
                        ],
                    },
                }

                features.append(feature)

            return {
                "type": "FeatureCollection",
                "features": features,
                "source": "OpenAQ",
                "fallback": False,
                "generated_at": datetime.now(
                    timezone.utc
                ),
            }

        except Exception as error:

            print(
                f"OpenAQ failed: {error}. "
                "Using fallback data."
            )

            fallback = load_fallback_data()

            return {
                "type": "FeatureCollection",
                "features": fallback["features"],
                "source": "Fallback",
                "fallback": True,
                "generated_at": datetime.now(
                    timezone.utc
                ),
            }

    @staticmethod
    def _timestamp(item: dict):
        datetime_data = item.get("datetime")

        if isinstance(datetime_data, dict):
            return (
                datetime_data.get("utc")
                or datetime_data.get("local")
            )

        return None