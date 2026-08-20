# app/main.py

import uvicorn
from fastapi import FastAPI
from app.routers import api, web

app = FastAPI(title="Kom-Way API")

# Include your routers
app.include_router(api.router)
app.include_router(web.router)


if __name__ == "__main__":
    '''
    Normally the app is running in Docker, but for debugging and development 
    the app can also be run via terminal using:
    (.venv) juraj@jplaptop:~/code/kom-way$ python -m app.main
    '''
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)