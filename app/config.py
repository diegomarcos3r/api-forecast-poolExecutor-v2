from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    with ProcessPoolExecutor(max_workers=6) as pool:
        app.state.pool_executor = pool
        print("✓ ProcessPoolExecutor inicializado")
        yield
    # Shutdown
    print("✓ ProcessPoolExecutor finalizado")
