import time

import requests

from app.config import WORLDPOP_BASE_URL


class WorldPopAdapter:
    def __init__(self):
        self.base_url = WORLDPOP_BASE_URL

    def population_for_polygon(
        self,
        geojson: dict,
        year: int = 2020,
        resolution: str = "1km",
    ) -> float:
        """
        Calculates population inside a GeoJSON Polygon/MultiPolygon.

        WorldPop v2 returns an asynchronous task.
        """

        payload = {
            "geojson": geojson,
            "year": year,
            "resolution": resolution,
        }

        response = requests.post(
            f"{self.base_url}/population",
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        task_id = response.json()["task_id"]

        for _ in range(20):
            result_response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                timeout=20,
            )

            result_response.raise_for_status()

            result = result_response.json()

            if result["status"] == "success":
                return float(
                    result["result"]["total_population"]
                )

            if result["status"] == "failure":
                raise RuntimeError(
                    result.get("error", "WorldPop task failed")
                )

            time.sleep(1)

        raise TimeoutError("WorldPop task timed out")