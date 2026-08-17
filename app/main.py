from fastapi import FastAPI
from app.routers.forecast_routes import forecast_router
from app.routers.health import health_router
from app.config import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(forecast_router)
app.include_router(health_router)