import logging
import socket
from contextlib import asynccontextmanager

from fastapi import FastAPI
from livemech.api.routers.shops import router as shops_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("App started on host: %s", socket.gethostname())
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(shops_router)

@app.get("/")
def read_root():
    hostname = socket.gethostname()
    return {"Hello": "Maun", "Host": hostname}