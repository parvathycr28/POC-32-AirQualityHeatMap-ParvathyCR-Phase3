from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AirQualityProperties(BaseModel):
    city: str
    pollutant: str
    value: float
    unit: str
    timestamp: Optional[datetime] = None
    population: Optional[int] = None
    exposure_score: Optional[float] = None
    regional_average: Optional[float] = None
    percentage_above_average: Optional[float] = None
    source: str = "OpenAQ"


class GeoJSONPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="[longitude, latitude]",
    )


class AirQualityFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONPoint
    properties: AirQualityProperties


class AirQualityResponse(BaseModel):
    type: str = "FeatureCollection"
    data_source: str
    features: List[AirQualityFeature]


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float
    pollutant: str
    unit: str


class CitySummary(BaseModel):
    city: str
    pollutant: str
    value: float
    unit: str
    exposure_score: Optional[float] = None
    population: Optional[int] = None


class ComparisonResponse(BaseModel):
    cities: List[CitySummary]


class InsightResponse(BaseModel):
    why_this_matters: str
    who_controls_the_rail: str