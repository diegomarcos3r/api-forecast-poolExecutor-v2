from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    pool = ProcessPoolExecutor(max_workers=6)
    app.state.pool_executor = pool
    print("✓ ProcessPoolExecutor inicializado")
    yield
    # Shutdown
    pool.shutdown(wait=True)
    print("✓ ProcessPoolExecutor finalizado")
