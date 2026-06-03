# app/main.py

from fastapi import FastAPI
from app.schemas.weather_schema import WeatherRequest, WeatherResponse, GarminWeatherResponse
from app.services.weather import process_weather_request

app = FastAPI(
    title="Kom-Way API",
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
    docs_url="/docs",
    redoc_url=None # Disables redoc to focus purely on fixing swagger
)


@app.get("/")
async def root_status():
    return {
        "status": "online",
        "message": "Kom-Way API service is up and running"
    }


@app.post("/api/v1/full-weather", response_model=WeatherResponse)
async def receive_full_weather(request: WeatherRequest):
    '''
    Full weather request with all detailed parameters
    '''
    return await process_weather_request(request)


@app.post("/api/v1/garmin-weather", response_model=GarminWeatherResponse)
async def receive_garmin_weather(request: WeatherRequest):
    '''
    Garmin specific weather request with memory optimisation and limited field returns (re-uses the full weather requests)
    '''
    full_weather = await process_weather_request(request)


    return GarminWeatherResponse(
        t=int(full_weather.time.timestamp()),
        ws=full_weather.wind_speed_kmh,
        wg=full_weather.wind_gust_kmh,
        wd=full_weather.wind_deg_rounded,
        temp=full_weather.temp_celsius,
        rain=full_weather.next_rain_total
    )