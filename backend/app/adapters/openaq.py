import requests

from app.config import OPENAQ_API_KEY, OPENAQ_BASE_URL


class OpenAQAdapter:
    def __init__(self):
        self.base_url = OPENAQ_BASE_URL
        self.headers = {
            "X-API-Key": OPENAQ_API_KEY or "",
        }

    def get_latest(self, parameter_id: int = 2, limit: int = 100):
        """
        OpenAQ parameter IDs:
        2 = PM2.5
        1 = PM10
        3 = O3
        5 = NO2
        """

        url = f"{self.base_url}/parameters/{parameter_id}/latest"

        response = requests.get(
            url,
            headers=self.headers,
            params={"limit": limit},
            timeout=20,
        )

        response.raise_for_status()

        return response.json()

    def get_locations(self, parameter_id: int = 2, limit: int = 100):
        url = f"{self.base_url}/locations"

        response = requests.get(
            url,
            headers=self.headers,
            params={
                "parameters_id": parameter_id,
                "limit": limit,
            },
            timeout=20,
        )

        response.raise_for_status()

        return response.json()