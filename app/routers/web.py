# app/routers/web.py

from fastapi import Request, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from collections import Counter

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
LOG_FILE = Path(__file__).parent.parent / "log" / "garmin_debug.log"
STATUS_SECRET_KEY = "juraj"
log_lines = 100

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/privacy")
async def privacy_policy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})

@router.get("/status")
async def status_dashboard(request: Request, key: str = None):
    if key != STATUS_SECRET_KEY:
        raise HTTPException(status_code=404, detail="Not found")

    logs = []
    status_counts = Counter()
    ip_counts = Counter()

    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if not entry:
                        continue
                    
                    if "time_local" not in entry:
                        entry["time_local"] = entry.get("time", "N/A")
                    if "status" not in entry:
                        entry["status"] = 200
                    if "ip" not in entry:
                        entry["ip"] = "unknown"
                    if "duration_ms" not in entry:
                        entry["duration_ms"] = 0.0
                    if "in" not in entry or not isinstance(entry["in"], dict):
                        entry["in"] = {"latitude": 0.0, "longitude": 0.0}
                    if "out" not in entry or not isinstance(entry["out"], dict):
                        entry["out"] = {"ws": 0.0, "temp": 0.0}

                    status_counts[entry["status"]] += 1
                    ip_counts[entry["ip"]] += 1
                    
                    logs.append(entry)
                except (json.JSONDecodeError, ValueError):
                    pass

    logs.reverse()

    return templates.TemplateResponse(
        "status.html", 
        {
            "request": request, 
            "logs": logs,
            "status_counts": dict(status_counts.most_common()),
            "unique_ip_count": len(ip_counts)  # [MODIFIED] Pass unique count instead of full dict
        }
    )