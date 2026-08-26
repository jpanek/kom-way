# app/routers/web.py

from fastapi import Request, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.database import execute_query

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
LOG_FILE = Path(__file__).parent.parent / "log" / "garmin_debug.log"
STATUS_SECRET_KEY = "juraj"
LOG_HISTORY_DAYS = 3
log_lines = 300

LOGS_QUERY = """
    SELECT time_local, status, ip, duration_ms, latitude, longitude, ws, temp
    FROM api_logs
    WHERE created_at >= NOW() - INTERVAL '1 day' * %s
    ORDER BY created_at DESC
    limit 100;
"""

STATUS_COUNTS_QUERY = """
    SELECT status, COUNT(*) as count
    FROM api_logs
    WHERE created_at >= NOW() - INTERVAL '1 day' * %s
    GROUP BY status
    ORDER BY count DESC;
"""

UNIQUE_IPS_QUERY = """
    SELECT COUNT(DISTINCT ip) as unique_ips
    FROM api_logs
    WHERE created_at >= NOW() - INTERVAL '1 day' * %s;
"""

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

    logs = execute_query(LOGS_QUERY, (LOG_HISTORY_DAYS,), fetch="all")
    status_rows = execute_query(STATUS_COUNTS_QUERY, (LOG_HISTORY_DAYS,), fetch="all")
    unique_ip_row = execute_query(UNIQUE_IPS_QUERY, (LOG_HISTORY_DAYS,), fetch="one")

    status_counts = {row["status"]: row["count"] for row in status_rows}
    unique_ip_count = unique_ip_row["unique_ips"] if unique_ip_row else 0

    return templates.TemplateResponse(
        "status.html", 
        {
            "request": request, 
            "logs": logs,
            "status_counts": status_counts,
            "unique_ip_count": unique_ip_count
        }
    )