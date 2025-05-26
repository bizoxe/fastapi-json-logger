import atexit
import logging
import logging.config
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from utils.json_logger.json_log_formatter import JSONLogFormatter
from utils.json_logger.log_handlers import CustomQueueHandler
from utils.json_logger.middlewares import LoggingMiddleware

BASE_DIR = Path(__file__).absolute().parent.parent
TEST_LOG_DIR = BASE_DIR / "test_log"


logger = logging.getLogger("test_2")


@pytest.fixture(scope="function")
def cleen_up_log_files():
    directory = TEST_LOG_DIR
    TEST_LOG_DIR.mkdir(exist_ok=True)
    yield

    for item in directory.iterdir():
        if item.is_file():
            item.unlink()

    TEST_LOG_DIR.rmdir()


@pytest.fixture
def get_log_dir():
    return TEST_LOG_DIR


class MyException(Exception):
    pass


@pytest.fixture
def app() -> FastAPI:
    _app = FastAPI()
    _app.middleware("http")(LoggingMiddleware())

    @_app.get("/")
    def index():
        return {"message": "Hello world from FastAPI app"}

    @_app.get("/error")
    def error():
        raise MyException
        return {}

    @_app.get("/levels/debug")
    def log_debug():
        logger.debug("Debug message")
        return {}

    @_app.get("/levels/info")
    def log_info():
        logger.info("Info message")
        return {}

    @_app.get("/levels/exception")
    def log_exception():
        try:
            raise MyException
        except MyException as err:
            logger.exception("An error occurred", exc_info=err)
        return {}

    @_app.get("/levels/critical")
    def log_critical():
        logger.critical("Critical message")
        return {}

    @_app.get("/public")
    def public():
        logger.info(
            "User %(username)s and %(password)s",
            {"username": "Elena", "password": "secretpwd"},
        )
        return {"message": "success"}

    return _app


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_middleware_logger(mocker) -> None:
    mocker.patch("utils.json_logger.middlewares.logger", logging.getLogger("test"))


@pytest.fixture(scope="function")
def disable_loggers_during_tests():
    list_loggers = ["httpx", "asyncio"]
    for l in list_loggers:
        logging.getLogger(l).disabled = True


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": JSONLogFormatter,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "level": "DEBUG",
        },
        "file_handler": {
            "level": "INFO",
            "filename": f"{TEST_LOG_DIR}/test_log.jsonl",
            "class": "logging.handlers.RotatingFileHandler",
            "encoding": "utf8",
        },
        "queue_handler": {
            "class": CustomQueueHandler,
            "listener": "logging.handlers.QueueListener",
            "formatter": "json",
            "queue": {
                "()": "multiprocessing.Queue",
                "maxsize": 1000,
            },
            "level": "DEBUG",
            "handlers": ["console", "file_handler"],
            "respect_handler_level": True,
        },
    },
    "loggers": {
        "test": {
            "handlers": ["queue_handler"],
            "level": "DEBUG",
            "propagate": False,
        },
        "test_2": {
            "handlers": ["queue_handler"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


@pytest.fixture(scope="function")
def prepare_logging(cleen_up_log_files):
    logging.config.dictConfig(LOG_CONFIG)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
