from fastapi import APIRouter, Request
from app.models.models import CreateSimulation
from typing import Dict
from app.services.forecast import Forecast



# instanciar classe para criação da API

forecast_router = APIRouter(prefix="/forecast", tags=["forecast"])


# Endpoints

@forecast_router.post("/run-forecast")
async def create_simulation(request: Request, new_simulation: CreateSimulation) -> dict:

    forecast = Forecast(
        nr_simulations = new_simulation.nr_simulations,
        backlog_min = new_simulation.backlog_min,
        backlog_max = new_simulation.backlog_max,
        capacity = new_simulation.capacity,
        throughput = new_simulation.throughput,
        pool_executor = request.app.state.pool_executor
    )

    result = await forecast.run_forecast()

    return result
