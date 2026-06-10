# app/routers/api.py

from fastapi import APIRouter
from app.schemas.weather_schema import WeatherRequest, WeatherResponse, GarminWeatherResponse
from app.services.weather import process_weather_request

router = APIRouter(prefix="/api/v1")

@router.post("/full-weather", response_model=WeatherResponse)
async def receive_full_weather(request: WeatherRequest):
    '''
    Full weather request with all detailed parameters
    '''
    return await process_weather_request(request)

@router.post("/garmin-weather", response_model=GarminWeatherResponse)
async def receive_garmin_weather(request: WeatherRequest):
    '''
    Garmin specific weather request with memory optimisation and limited field returns (re-uses the full weather requests)
    '''
    full_weather = await process_weather_request(request)


    return GarminWeatherResponse(
        t=full_weather.time_unix,
        int=full_weather.interval,
        ws=full_weather.wind_speed_kmh,
        wg=full_weather.wind_gust_kmh,
        wd=full_weather.wind_deg,
        wdr=full_weather.wind_deg_rounded,
        temp=full_weather.temp_celsius,
        rain=full_weather.next_rain_total
    )
