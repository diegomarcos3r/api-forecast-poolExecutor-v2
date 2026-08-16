from fastapi import FastAPI
from app.routers.forecast_routes import forecast_router
from app.routers.health import health_router

app = FastAPI()

app.include_router(forecast_router)
app.include_router(health_router)