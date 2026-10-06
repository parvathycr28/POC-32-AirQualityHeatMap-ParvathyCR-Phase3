const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8001";

export type AirQualityFeature = {
  type: "Feature";

  properties: {
    city: string;
    country: string;
    pollutant: string;
    value: number;
    unit: string;
    timestamp: string;
    population?: number;
    exposure_score?: number;
    regional_average?: number;
    percentage_above_regional_average?: number;
    source?: string;
    fallback?: boolean;
    generated_at?: string;
  };

  geometry: {
    type: "Point";
    coordinates: [number, number];
  };
};

export type AirQualityResponse = {
  type: "FeatureCollection";

  features: AirQualityFeature[];

  fallback?: boolean;

  generated_at?: string;
};

export async function getAirQuality(
  pollutant: string = "pm25"
): Promise<AirQualityResponse> {
  const response = await fetch(
    `${API_URL}/api/air-quality?pollutant=${encodeURIComponent(
      pollutant
    )}`,
    {
      cache: "no-store",
    }
  );

  
if (!response.ok) {
  let message = `Air quality request failed: ${response.status}`;

  try {
    const errorBody = await response.json();

    if (errorBody?.detail) {
      message =
        typeof errorBody.detail === "string"
          ? errorBody.detail
          : JSON.stringify(errorBody.detail);
    }
  } catch {
    // Keep the default HTTP error message.
  }

  throw new Error(message);
}



  return response.json();
}
export async function getPopulation(
  latitude: number,
  longitude: number
): Promise<number | null> {
  const response = await fetch(
    `${API_URL}/api/population?latitude=${encodeURIComponent(
      latitude
    )}&longitude=${encodeURIComponent(longitude)}`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    return null;
  }

  const data = await response.json();

  return typeof data.population === "number"
    ? data.population
    : null;
}