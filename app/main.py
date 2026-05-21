# app/main.py

from fastapi import FastAPI
from app.schemas.weather_schema import WeatherRequest, WeatherResponse
from app.services.weather import process_weather_request

app = FastAPI(
    title="Kom-Way API",
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
    docs_url="/docs",
    redoc_url=None # Disables redoc to focus purely on fixing swagger
)

"""
@app.get("/")
async def root_status():
    return {
        "status": "online",
        "message": "Kom-Way API service is up and running"
    }
"""

@app.post("/api/v1/weather-check", response_model=WeatherResponse)
async def receive_weather_coords(request: WeatherRequest):
    return await process_weather_request(request)