import json
import math
import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="Air Quality Intelligence API")

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

OPENAQ_BASE_URL = "https://api.openaq.org/v3"
WORLDPOP_URL = "https://api.worldpop.org/v1/services/stats"
WORLDPOP_YEAR = 2020
WORLDPOP_RESOLUTION = os.getenv(
    "WORLDPOP_RESOLUTION",
    "1km",
)

BASE_DIR = Path(__file__).resolve().parent

MOCK_FILE = BASE_DIR / "mock_data.json"
OPENAQ_POLLUTANTS = {
    "pm25": {
        "id": 2,
        "name": "PM2.5",
        "unit": "µg/m³",
        "score_reference": 55.2,
    },
    "pm2.5": {
        "id": 2,
        "name": "PM2.5",
        "unit": "µg/m³",
        "score_reference": 55.2,
    },
    "pm10": {
        "id": 1,
        "name": "PM10",
        "unit": "µg/m³",
        "score_reference": 100.0,
    },
    "no2": {
        "id": 7,
        "name": "NO₂",
        "unit": "ppm",
        "score_reference": 0.100,
    },
    "co": {
        "id": 8,
        "name": "CO",
        "unit": "ppm",
        "score_reference": 9.0,
    },
    "so2": {
        "id": 9,
        "name": "SO₂",
        "unit": "ppm",
        "score_reference": 0.075,
    },
    "o3": {
        "id": 10,
        "name": "O₃",
        "unit": "ppm",
        "score_reference": 0.070,
    },
}
def get_pollutant_config(pollutant: str) -> dict[str, Any]:
    pollutant_key = pollutant.lower().strip()

    config = OPENAQ_POLLUTANTS.get(pollutant_key)

    if config is None:
        raise ValueError(
            f"Unsupported pollutant: {pollutant}"
        )

    return config
# Regional reference used by your existing dashboard.
REGIONAL_AVERAGE_PM25 = 55.2

WORLDPOP_CACHE: dict[tuple[float, float], float | None] = {}


def load_mock_data() -> dict[str, Any]:
    with open(MOCK_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def percentage_difference(
    value: float,
    reference: float,
) -> float:
    if reference == 0:
        return 0

    return round(
        ((value - reference) / reference) * 100,
        1,
    )

def calculate_exposure_score(
    value: float,
    score_reference: float,
) -> int:
    if score_reference <= 0:
        return 0

    score = (value / score_reference) * 50

    return max(
        0,
        min(
            100,
            round(score),
        ),
    )

   

    return max(
        0,
        min(
            100,
            round(score),
        ),
    )


def make_point_feature(
    *,
    city: str,
    country: str,
    latitude: float,
    longitude: float,
    value: float,
    timestamp: str,
    population: int | None,
    source: str,
    pollutant: str,
) -> dict[str, Any]:

    config = get_pollutant_config(pollutant)

    pollutant_name = config["name"]
    pollutant_unit = config["unit"]
    regional_average = config["score_reference"]

    exposure_score = calculate_exposure_score(
        value,
        regional_average,config["score_reference"],
    )

    

    percentage_above_regional_average = (
        percentage_difference(
            value,
            regional_average,
        )
    )

    return {
        "type": "Feature",
        "properties": {
            "city": city,
            "country": country,
            "pollutant": config["name"],
            "value": round(value, 4),
            "unit": config["unit"],
            "timestamp": timestamp,
            "population": population,
            "exposure_score": exposure_score,
            "regional_average": regional_average,
            "percentage_above_regional_average": (
                percentage_above_regional_average
            ),
            "source": source,
        },
        "geometry": {
            "type": "Point",
            "coordinates": [
                longitude,
                latitude,
            ],
        },
    }


async def get_worldpop_population(
    latitude: float,
    longitude: float,
) -> float | None:

    delta = 0.025

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                longitude - delta,
                                latitude - delta,
                            ],
                            [
                                longitude + delta,
                                latitude - delta,
                            ],
                            [
                                longitude + delta,
                                latitude + delta,
                            ],
                            [
                                longitude - delta,
                                latitude + delta,
                            ],
                            [
                                longitude - delta,
                                latitude - delta,
                            ],
                        ]
                    ],
                },
            }
        ],
    }

    params = {
        "dataset": "wpgppop",
        "year": WORLDPOP_YEAR,
        "geojson": json.dumps(geojson),
        "runasync": "false",
    }

    try:
        async with httpx.AsyncClient(
            timeout=60
        ) as client:

            response = await client.get(
                WORLDPOP_URL,
                params=params,
            )

            print(
                "WORLDPOP STATUS:",
                response.status_code,
            )

            print(
                "WORLDPOP RESPONSE:",
                response.text[:5000],
            )

            response.raise_for_status()

            data = response.json()

        if data.get("error"):
            print(
                "WORLDPOP ERROR:",
                data.get("error_message"),
            )

            return None

        population = (
            data
            .get("data", {})
            .get("total_population")
        )

        print(
            "WORLDPOP POPULATION:",
            population,
            "AT:",
            latitude,
            longitude,
        )

        if population is None:
            print(
                "WORLDPOP: total_population not found"
            )

            return None

        return float(population)

    except Exception as error:

        print(
            "WORLDPOP REQUEST ERROR:",
            repr(error),
        )

        return None


async def get_cached_worldpop_population(
    latitude: float,
    longitude: float,
) -> float | None:

    # Round coordinates so extremely tiny coordinate
    # differences don't create unnecessary API requests.
    cache_key = (
        round(latitude, 3),
        round(longitude, 3),
    )

    if cache_key in WORLDPOP_CACHE:
        return WORLDPOP_CACHE[cache_key]

    population = await get_worldpop_population(
        latitude,
        longitude,
    )

    WORLDPOP_CACHE[cache_key] = population

    return population


async def get_openaq_latest(
    parameter_id: int,
) -> list[dict[str, Any]]:

    if not OPENAQ_API_KEY:
        raise RuntimeError(
            "OPENAQ_API_KEY is missing from backend/.env"
        )

    headers = {
        "X-API-Key": OPENAQ_API_KEY,
    }

    results: list[dict[str, Any]] = []

    async with httpx.AsyncClient(
        timeout=30,
        headers=headers,
    ) as client:

        response = await client.get(
            f"{OPENAQ_BASE_URL}/parameters/"
            f"{parameter_id}/latest",
            params={
                "limit": 200,
                "page": 1,
            },
        )

        if response.status_code == 429:
            raise RuntimeError(
                "OpenAQ rate limit reached (HTTP 429)."
            )

        if response.status_code >= 500:
            raise RuntimeError(
                f"OpenAQ server error: "
                f"HTTP {response.status_code}."
            )

        response.raise_for_status()

        payload = response.json()

        results.extend(
            payload.get("results", [])
        )

    print(
        f"OpenAQ measurements fetched: "
        f"{len(results)}"
    )

    return results


async def get_openaq_locations(
    parameter_id: int,
) -> dict[int, dict[str, Any]]:

    if not OPENAQ_API_KEY:
        raise RuntimeError(
            "OPENAQ_API_KEY is missing from backend/.env"
        )

    headers = {
        "X-API-Key": OPENAQ_API_KEY,
    }

    locations: dict[int, dict[str, Any]] = {}

    page = 1
    max_pages = 20

    async with httpx.AsyncClient(
        timeout=30,
        headers=headers,
    ) as client:

        while page <= max_pages:

            response = await client.get(
                f"{OPENAQ_BASE_URL}/locations",
                params={
                    "parameters_id": parameter_id,
                    "limit": 1000,
                    "page": page,
                },
            )

            # OpenAQ can occasionally return a server error
            # on a later page. Keep locations already retrieved.
            if response.status_code >= 500:
                print(
                    f"OpenAQ locations returned "
                    f"{response.status_code} on page {page}. "
                    f"Stopping pagination."
                )

                break

            response.raise_for_status()

            payload = response.json()

            page_results = payload.get(
                "results",
                [],
            )

            if not page_results:
                break

            for location in page_results:

                location_id = location.get("id")

                if location_id is None:
                    continue

                locations[int(location_id)] = location

            print(
                f"OpenAQ locations: page {page}, "
                f"total collected: {len(locations)}"
            )

            meta = payload.get(
                "meta",
                {},
            )

            found = meta.get("found")

            # OpenAQ can return values such as ">1000".
            # Do not blindly call int(found).
            try:
                found_int = int(found)
            except (
                TypeError,
                ValueError,
            ):
                found_int = None

            if (
                found_int is not None
                and len(locations) >= found_int
            ):
                break

            page += 1

    print(
        f"Total OpenAQ locations fetched for "
        f"parameter {parameter_id}: "
        f"{len(locations)}"
    )

    return locations


async def get_openaq_locations(
    parameter_id: int,
) -> dict[int, dict[str, Any]]:

    if not OPENAQ_API_KEY:
        raise RuntimeError(
            "OPENAQ_API_KEY is missing from backend/.env"
        )

    headers = {
        "X-API-Key": OPENAQ_API_KEY,
    }

    locations: dict[int, dict[str, Any]] = {}

    page = 1

    async with httpx.AsyncClient(
        timeout=30,
        headers=headers,
    ) as client:

        while True:

            response = await client.get(
                f"{OPENAQ_BASE_URL}/locations",
                params={
                    "parameters_id": parameter_id,
                    "limit": 1000,
                    "page": page,
                },
            )

            # OpenAQ can occasionally return a server error
            # on a later page. Keep successfully retrieved locations.
            if response.status_code >= 500:
                print(
                    f"OpenAQ locations returned "
                    f"{response.status_code} on page {page}. "
                    f"Stopping pagination."
                )

                break

            response.raise_for_status()

            payload = response.json()

            page_results = payload.get(
                "results",
                [],
            )

            if not page_results:
                break

            for location in page_results:

                location_id = location.get("id")

                if location_id is None:
                    continue

                locations[int(location_id)] = location

            meta = payload.get(
                "meta",
                {},
            )

            found = meta.get("found")

            if found is None:
                break

            # OpenAQ can return values such as ">1000".
            # Only convert found to an integer when possible.
            try:
                found_int = int(found)
            except (
                TypeError,
                ValueError,
            ):
                found_int = None

            if (
                found_int is not None
                and len(locations) >= found_int
            ):
                break

            page += 1

            # Safety limit.
            if page > 20:
                break

    return locations


async def get_location_name(
    client: httpx.AsyncClient,
    location_id: int,
) -> tuple[str, str]:

    try:

        response = await client.get(
            f"{OPENAQ_BASE_URL}/locations/{location_id}"
        )

        response.raise_for_status()

        location = response.json().get(
            "results",
            [],
        )

        if not location:
            return (
                "Unknown location",
                "Unknown",
            )

        location = location[0]

        name = (
            location.get("locality")
            or location.get("name")
            or "Unknown location"
        )

        country = (
            location.get("country", {}).get("name")
            or "Unknown"
        )

        return name, country

    except Exception as error:

        print(
            f"OpenAQ location lookup failed "
            f"for {location_id}:",
            error,
        )

        return (
            "Unknown location",
            "Unknown",
        )


async def build_live_geojson(
    parameter_id: int,
    pollutant_name: str,
    pollutant_unit: str,
    score_reference: float,
    pollutant_key: str,
) -> dict[str, Any]:

    measurements = await get_openaq_latest(
        parameter_id
    )

    if not measurements:
        raise RuntimeError(
            f"No measurements available for "
            f"{pollutant_name}."
        )

    try:
        locations = await get_openaq_locations(
            parameter_id
        )
    except Exception as error:
        print(
            "OpenAQ location lookup failed:",
            repr(error),
        )
        locations = {}

    features: list[dict[str, Any]] = []

    for measurement in measurements:

        coordinates = measurement.get(
            "coordinates"
        )

        if not coordinates:
            continue

        latitude = coordinates.get(
            "latitude"
        )

        longitude = coordinates.get(
            "longitude"
        )

        if not isinstance(
            latitude,
            (int, float),
        ):
            continue

        if not isinstance(
            longitude,
            (int, float),
        ):
            continue

        value = measurement.get("value")

        if value is None:
            continue

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            continue

        if not math.isfinite(value):
            continue

        location_id = measurement.get(
            "locationsId"
        )

        location = None

        if location_id is not None:
            try:
                location = locations.get(
                    int(location_id)
                )
            except (
                TypeError,
                ValueError,
            ):
                location = None

        location_name = (
            location.get("name")
            if location
            else None
        )

        locality = (
            location.get("locality")
            if location
            else None
        )

        country_data = (
            location.get("country")
            if location
            else None
        )

        if isinstance(
            country_data,
            dict,
        ):
            country_name = (
                country_data.get("name")
                or "Unknown"
            )

            country_code = (
                country_data.get("code")
                or ""
            )
        else:
            country_name = "Unknown"
            country_code = ""

        city_name = (
            locality
            or location_name
            or (
                f"OpenAQ Location {location_id}"
                if location_id is not None
                else "OpenAQ Measurement"
            )
        )

        timestamp_data = measurement.get(
            "datetime",
            {},
        )

        if isinstance(
            timestamp_data,
            dict,
        ):
            timestamp = (
                timestamp_data.get("utc")
                or ""
            )
        else:
            timestamp = ""

        exposure_score = calculate_exposure_score(
            value,
            score_reference,
        )

        regional_average = score_reference

        percentage_above_regional_average = (
            percentage_difference(
                value,
                regional_average,
            )
        )

        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        longitude,
                        latitude,
                    ],
                },
                "properties": {
                    "city": city_name,
                    "country": country_name,

                    # Selected pollutant
                    "pollutant": pollutant_name,

                    # Actual measurement
                    "value": round(
                        value,
                        4,
                    ),

                    # Selected pollutant unit
                    "unit": pollutant_unit,

                    "population": None,

                    # Score calculated for selected pollutant
                    "exposure_score": (
                        exposure_score
                    ),

                    # Reference for selected pollutant
                    "regional_average": (
                        regional_average
                    ),

                    "percentage_above_regional_average": (
                        percentage_above_regional_average
                    ),

                    "timestamp": timestamp,

                    "source": "OpenAQ",

                    "locationId": location_id,

                    "countryCode": country_code,
                },
            }
        )

    print(
        f"{pollutant_name}: "
        f"GeoJSON features created: "
        f"{len(features)}"
    )

    return {
        "type": "FeatureCollection",
        "features": features,
        "pollutant": pollutant_key,
        "pollutantName": pollutant_name,
        "unit": pollutant_unit,
    }
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Air Quality Intelligence API",
    }

def build_fallback_geojson(
    pollutant: str,
) -> dict[str, Any]:

    config = get_pollutant_config(
        pollutant
    )

    mock_data = load_mock_data()

    reference = config["score_reference"]

    factors = {
        "pm25": 1.00,
        "pm10": 1.35,
        "no2": 0.0008,
        "co": 0.012,
        "so2": 0.0004,
        "o3": 0.001,
    }

    factor = factors.get(
        pollutant,
        1.0,
    )

    features: list[dict[str, Any]] = []

    for index, original in enumerate(
        mock_data.get("features", [])
    ):

        properties = original.get(
            "properties",
            {},
        )

        geometry = original.get(
            "geometry",
            {},
        )

        coordinates = geometry.get(
            "coordinates",
            [],
        )

        if (
            not isinstance(coordinates, list)
            or len(coordinates) < 2
        ):
            continue

        original_value = properties.get(
            "value",
            reference,
        )

        try:
            original_value = float(
                original_value
            )
        except (
            TypeError,
            ValueError,
        ):
            original_value = reference

        if pollutant == "pm25":
            value = original_value
        else:
            # Synthetic fallback values.
            # These are NOT official measurements.
            value = (
                reference
                * (
                    original_value
                    / 55.2
                )
                * factor
            )

        value = max(
            0,
            float(value),
        )

        exposure_score = (
            calculate_exposure_score(
                value,
                reference,
            )
        )

        percentage = (
            percentage_difference(
                value,
                reference,
            )
        )

        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": coordinates,
                },
                "properties": {
                    "city": (
                        properties.get(
                            "city"
                        )
                        or f"Fallback Location {index + 1}"
                    ),
                    "country": (
                        properties.get(
                            "country"
                        )
                        or "Unknown"
                    ),
                    "pollutant": config[
                        "name"
                    ],
                    "value": round(
                        value,
                        4,
                    ),
                    "unit": config[
                        "unit"
                    ],
                    "timestamp": (
                        properties.get(
                            "timestamp"
                        )
                        or ""
                    ),
                    "population": (
                        properties.get(
                            "population"
                        )
                    ),
                    "exposure_score": (
                        exposure_score
                    ),
                    "regional_average": (
                        reference
                    ),
                    "percentage_above_regional_average": (
                        percentage
                    ),
                    "source": "Synthetic fallback",
                    "fallback": True,
                },
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
        "pollutant": pollutant,
        "pollutantName": config[
            "name"
        ],
        "unit": config[
            "unit"
        ],
        "fallback": True,
    }
@app.get("/api/air-quality")
async def air_quality(
    pollutant: str = Query("pm25"),
):
    pollutant_key = pollutant.lower().strip()

    # Treat pm2.5 as the same internal pollutant as pm25.
    if pollutant_key == "pm2.5":
        pollutant_key = "pm25"

    pollutant_config = OPENAQ_POLLUTANTS.get(
        pollutant_key
    )

    if pollutant_config is None:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported pollutant.",
                "supported": [
                    "pm25",
                    "pm10",
                    "no2",
                    "co",
                    "so2",
                    "o3",
                ],
            },
        )

    parameter_id = pollutant_config["id"]

    try:
        data = await build_live_geojson(
            parameter_id=parameter_id,
            pollutant_name=pollutant_config["name"],
            pollutant_unit=pollutant_config["unit"],
            score_reference=pollutant_config[
                "score_reference"
            ],
            pollutant_key=pollutant_key,
        )

        if not data.get("features"):
            raise RuntimeError(
                "OpenAQ returned no usable measurements."
            )

        return data

    except Exception as error:

        print(
            "OpenAQ failed. Using fallback data:",
            repr(error),
        )

        return build_fallback_geojson(
            pollutant_key
        )

@app.get("/api/population")
async def population(
    latitude: float,
    longitude: float,
):

    value = await get_worldpop_population(
        latitude=latitude,
        longitude=longitude,
    )

    if value is None:

        raise HTTPException(
            status_code=502,
            detail="WorldPop population data unavailable.",
        )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "population": value,
        "source": "WorldPop",
        "year": WORLDPOP_YEAR,
        "resolution": WORLDPOP_RESOLUTION,
    }