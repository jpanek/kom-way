# schemas/weather_schema.py
from pydantic import BaseModel, Field, computed_field
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
    next_rain: list[float]

    @computed_field
    @property
    def next_rain_total(self) -> float:
        """
        Sums up all precipitation values in the upcoming intervals.
        Safely filters out any missing data or accidental None values.
        """
        if not self.next_rain:
            return 0.0
            
        total = sum(
            float(amount) 
            for amount in self.next_rain 
            if amount is not None and isinstance(amount, (int, float))
        )
        return round(total, 2)

    @computed_field
    @property
    def rain_imminent(self) -> bool:
        """Returns True if any non-zero precipitation is detected in the upcoming intervals."""
        return any(amount > 0.0 for amount in self.next_rain if amount is not None)

    @computed_field
    @property
    def minutes_until_rain(self) -> int | None:
        """
        Calculates how many minutes remain until the first drop of rain.
        Returns None if no rain is forecast in the current window.
        """
        for index, amount in enumerate(self.next_rain):
            if amount is not None and amount > 0.0:
                # Each index step represents a 15-minute block
                return index * 15
        return None
    
class GarminWeatherResponse(BaseModel):
    t: int          # time
    ws: float           # wind_speed_kmh
    wg: float           # wind_gust_kmh
    wd: float           # wind_deg_rounded
    temp: float         # temp_celsius
    rain: float         # next_rain_total