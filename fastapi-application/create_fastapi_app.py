from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from utils.json_logger.setup import setup_logging
from utils.json_logger.middlewares import LoggingMiddleware
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    queue_handler = logging.getHandlerByName("queue_handler")
    queue_handler.listener.start()

    yield
    queue_handler.listener.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api.name,
        version=settings.api.version,
        lifespan=lifespan,
    )
    app.middleware("http")(LoggingMiddleware())

    return app
