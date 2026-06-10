# app/main.py

import uvicorn
from fastapi import FastAPI
from app.routers import api, web

app = FastAPI(title="Kom-Way API")

# Include your routers
app.include_router(api.router)
app.include_router(web.router)

@app.get("/")
async def root_status():
    return {"status": "online"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)