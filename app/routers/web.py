# app/routers/web.py

from fastapi import Request, APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/privacy")
async def privacy_policy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})