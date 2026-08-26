# app/routers/web.py

from fastapi import Request, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from collections import Counter, deque

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
LOG_FILE = Path(__file__).parent.parent / "log" / "garmin_debug.log"
STATUS_SECRET_KEY = "juraj"
log_lines = 300

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

    # Get only the last 100 raw lines from disk
    raw_lines = tail_file(LOG_FILE, n=log_lines)

    for line in raw_lines:
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
            "unique_ip_count": len(ip_counts)
        }
    )

def tail_file(file_path, n=100):
    """Reads the last n lines of a file efficiently without loading the whole thing."""
    if not file_path.exists():
        return []

    with open(file_path, "rb") as f:
        f.seek(0, 2)  # Go to the end of the file
        file_size = f.tell()
        
        buffer_size = 1024
        lines = []
        data = bytearray()
        
        while file_size > 0 and len(lines) <= n:
            # Move back by buffer_size
            chunk_size = min(buffer_size, file_size)
            file_size -= chunk_size
            f.seek(file_size)
            data[0:0] = f.read(chunk_size)
            lines = data.splitlines()
            
        # Take the last n lines and decode back to utf-8 strings
        return [line.decode("utf-8", errors="ignore") for line in lines[-n:]]