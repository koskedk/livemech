import logging
import socket
import subprocess
from contextlib import asynccontextmanager

from fastapi import FastAPI
from livemech.api.routers.shops import router as shops_router

# 1. Configure logging so INFO messages actually print to the console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run Alembic migrations safely in a separate process."""
    logger.info("Running database migrations...")
    try:
        # 2. Run the CLI command via subprocess to avoid async event loop clashes
        subprocess.run(["uv", "run", "alembic", "upgrade", "head"], check=True)
        logger.info("Database migrations complete.")
    except subprocess.CalledProcessError as e:
        logger.error("Migrations failed to execute!")
        raise e

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("App started on host: %s", socket.gethostname())
    
    # Run the migrations
    run_migrations()
    
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(shops_router)

@app.get("/")
def read_root():
    hostname = socket.gethostname()
    return {"Hello": "Maun", "Host": hostname}