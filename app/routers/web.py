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
    # Lock down the route unless the correct secret key is passed in the URL
    if key != STATUS_SECRET_KEY:
        raise HTTPException(status_code=404, detail="Not found")  # Returns a 404 so it looks like it doesn't exist
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
                    
                    # [SAFE FALLBACKS for old log formats]
                    if "time_local" not in entry:
                        entry["time_local"] = entry.get("time", "N/A")
                    if "status" not in entry:
                        entry["status"] = 200
                    if "ip" not in entry:
                        entry["ip"] = "unknown"

                    status_counts[entry["status"]] += 1
                    ip_counts[entry["ip"]] += 1
                    
                    logs.append(entry)
                except (json.JSONDecodeError, ValueError):
                    pass

    logs.reverse()  # Newest first

    return templates.TemplateResponse(
        "status.html", 
        {
            "request": request, 
            "logs": logs,
            "status_counts": dict(status_counts.most_common()),
            "ip_counts": dict(ip_counts.most_common())
        }
    )