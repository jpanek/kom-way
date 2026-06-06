# app/services/weather.py
import os, json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import httpx
from fastapi import HTTPException
from app.schemas.weather_schema import WeatherRequest, WeatherResponse

def get_wind_direction(degrees: float):
    """Translates compass degrees (0-360) into standard 16-point text abbreviations."""
    directions = [
        "N", "NNE", "NE", "ENE", 
        "E", "ESE", "SE", "SSE", 
        "S", "SSW", "SW", "WSW", 
        "W", "WNW", "NW", "NNW"
    ]
    # Normalize degrees to safety zone [0, 360)
    deg = float(degrees) % 360
    
    # Divide into 16 segments of 22.5 degrees, offset by 11.25 to center the labels
    idx = int((deg + 11.25) / 22.5) % 16
    return {
        "text": directions[idx], 
        "degrees": degrees,
        "degrees_rounded": idx*22.5
    }

def sum_numeric_values(sequence) -> float:
    """
    Sums all numeric values in a given list or sequence.
    Safely ignores None values, strings, or other non-numeric types.
    """
    if not sequence:
        return 0.0
        
    return sum(
        float(item) 
        for item in sequence 
        if item is not None and isinstance(item, (int, float))
    )

async def process_weather_request(request: WeatherRequest) -> WeatherResponse:
    print(f"--> [Service] Processing weather for coordinates: {request.latitude}, {request.longitude}")

    next_15_min_period = 4
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": request.latitude,
        "longitude": request.longitude,
        "current": "temperature_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "minutely_15": "precipitation,wind_gusts_10m",
        "forecast_minutely_15": next_15_min_period,
        "wind_speed_unit": "kmh", 
        "timezone": "auto"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code != 200:
                print(f"--> [Error] Open-Meteo status {response.status_code}: {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch weather from Open-Meteo")
                
            data = response.json()
            
        except httpx.RequestError as exc:
            print(f"--> [Error] Network issue connecting to Open-Meteo: {exc}")
            raise HTTPException(status_code=503, detail="Open-Meteo weather service is unreachable")

    #current_data = data.get("current", {})
    #api_time_str = current_data.get("time")
    #api_time = datetime.fromisoformat(api_time_str).replace(tzinfo=timezone.utc)

    current_data = data.get("current", {})
    api_time_str = current_data.get("time")
    api_tz_name = data.get("timezone", "UTC")

    api_time_local = datetime.fromisoformat(api_time_str).replace(
        tzinfo=ZoneInfo(api_tz_name)
    )
    api_time = api_time_local.astimezone(timezone.utc)
    api_time_unix = int(api_time.timestamp())

    wind = get_wind_direction(current_data.get("wind_direction_10m", 0))

    
    #next_rain = sum_numeric_values(data.get("minutely_15", {}).get("precipitation", []))
    next_rain = data.get("minutely_15", {}).get("precipitation", [])
    #next_gust = data.get("minutely_15", {}).get("wind_gusts_10m",[])

    #print("data dump:")
    #print(json.dumps(data, indent=4))

    
    return WeatherResponse(
        status="success",
        lat=data.get("latitude", request.latitude),
        lon=data.get("longitude", request.longitude),
        time=api_time,
        time_unix=api_time_unix,
        interval = current_data.get("interval", 900),
        timezone = data.get("timezone"),
        timezone_code=data.get("timezone_abbreviation", "UTC"),
        wind_speed_kmh=current_data.get("wind_speed_10m", 0.0),
        wind_gust_kmh=current_data.get("wind_gusts_10m", 0.0),
        wind_deg_rounded=wind["degrees_rounded"],
        wind_deg=wind["degrees"],
        wind_dir=wind["text"],
        temp_celsius=current_data.get("temperature_2m", 0.0),
        next_rain = next_rain
    )