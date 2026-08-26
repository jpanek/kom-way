# app/routers/api.py

from fastapi import APIRouter, Request, Response
from app.schemas.weather_schema import WeatherRequest, WeatherResponse, GarminWeatherResponse
from app.services.weather import process_weather_request



router = APIRouter(prefix="/api/v1")

import json, time
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from pathlib import Path

# put garmin_debug.log right inside the app/ directory regardless of where uvicorn is launched
LOG_FILE = Path(__file__).parent.parent / "log" / "garmin_debug.log"
LOCAL_TZ = ZoneInfo("Europe/Prague")

def log_garmin_traffic(client_ip: str, status_code: int,req_data: dict, res_data: dict, duration_ms: float):
    now_utc = datetime.now(timezone.utc)
    log_entry = {
        "time_utc": now_utc.isoformat(),
        "time_local": now_utc.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "ip": client_ip,
        "status": status_code or 200,
        "duration_ms": duration_ms,
        "in": req_data,
        "out": res_data
    }
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

@router.post("/full-weather", response_model=WeatherResponse)
async def receive_full_weather(request: WeatherRequest):
    '''
    Full weather request with all detailed parameters
    '''
    return await process_weather_request(request)

@router.post("/garmin-weather", response_model=GarminWeatherResponse)
async def receive_garmin_weather(request: WeatherRequest, http_req: Request, response: Response):
    '''
    Garmin specific weather request with memory optimisation and limited field returns (re-uses the full weather requests)
    '''
    # Log incoming request data
    client_ip = http_req.headers.get("x-real-ip") or (http_req.client.host if http_req.client else "unknown")
    req_dict = request.model_dump()
    start_time = time.perf_counter()

    full_weather = await process_weather_request(request)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    response_data = GarminWeatherResponse(
        t=full_weather.time_unix,
        int=full_weather.interval,
        ws=full_weather.wind_speed_kmh,
        wg=full_weather.wind_gust_kmh,
        wd=full_weather.wind_deg,
        wdr=full_weather.wind_deg_rounded,
        temp=full_weather.temp_celsius,
        rain=sum(full_weather.next_rain) if full_weather.next_rain else 0.0
    )

    res_dict = response_data.model_dump()
    # Log both together in one row
    log_garmin_traffic(client_ip, response.status_code, req_dict, res_dict, duration_ms)

    return response_data
