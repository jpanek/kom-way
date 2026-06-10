# app/routers/web.py

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    with open("app/static/privacy.html", "r") as f:
        return f.read()