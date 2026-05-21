# schemas/weather_schema.py
from pydantic import BaseModel, Field
from datetime import datetime

# --- Input Models ---
class WeatherRequest(BaseModel):
    latitude: float = Field(default=50.103)
    longitude: float = Field(default=14.403)

# --- Output Models ---

class WeatherResponse(BaseModel):
    status: str
    lat: float
    lon: float
    time: datetime
    timezone: str
    timezone_code: str
    interval: float
    wind_speed_kmh: float
    wind_gust_kmh: float
    wind_deg: float
    wind_deg_rounded: float
    wind_dir: str
    temp_celsius: float
    next_rain: float