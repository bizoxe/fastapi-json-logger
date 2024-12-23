from contextlib import asynccontextmanager

from fastapi import FastAPI

from utils.json_logger.setup import setup_logging
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api.name,
        version=settings.api.version,
        lifespan=lifespan,
    )

    return app
