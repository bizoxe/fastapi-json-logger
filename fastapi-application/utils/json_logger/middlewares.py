"""
Logging middleware.
"""

from time import time
from math import ceil
import logging

from fastapi import (
    Request,
    Response,
)
from starlette.middleware.base import RequestResponseEndpoint
from starlette.background import BackgroundTask

from core.config import settings
from utils.json_logger.schemas import (
    RequestJsonLog,
    RequestSideSchema,
    ResponseSideSchema,
)


DEFAULT_HOST = settings.run.host
DEFAULT_PORT = settings.run.port
EMPTY_VALUE = ""
PASS_ROUTES = settings.log_cfg.pass_routes

logger = logging.getLogger("main")


async def get_protocol(request: Request) -> str:
    protocol = str(request.scope.get("type", ""))
    http_version = str(request.scope.get("http_version", ""))
    if protocol.lower() == "http" and http_version:
        return f"{protocol.upper()}/{http_version}"
    return EMPTY_VALUE


async def log(
    req_body: bytes,
    res_body: bytes,
    request: Request,
    response: Response,
    duration: int,
    exception_object: BaseException | None,
) -> None:
    """
    Initialises the fields of the RequestJsonLog schema and passes
    the object as an argument to the logger.
    """
    msg_type = "Response"
    log_level = 20
    server: tuple = request.get("server", (DEFAULT_HOST, DEFAULT_PORT))
    request_headers: dict = dict(request.headers.items())
    response_headers = dict(response.headers.items())
    if exception_object is not None:
        msg_type = "ERROR"
        log_level = 40
        response_headers = {}
    request_json_fields = RequestJsonLog(
        request=RequestSideSchema(
            request_uri=str(request.url),
            request_referer=request_headers.get("referer", EMPTY_VALUE),
            request_protocol=await get_protocol(request),
            request_method=request.method,
            request_path=request.url.path,
            request_host=f"{server[0]}:{server[1]}",
            request_size=int(request_headers.get("content-length", 0)),
            request_content_type=request_headers.get("content-type", EMPTY_VALUE),
            request_headers=dict(request_headers),
            request_body=req_body,
            request_direction="in",
            remote_ip=request.client[0],
            remote_port=request.client[1],
        ),
        response=ResponseSideSchema(
            response_status_code=response.status_code,
            response_size=int(response_headers.get("content-length", 0)),
            response_headers=dict(response_headers),
            response_body=res_body,
        ),
        duration=duration,
    ).model_dump()
    logger.log(
        level=log_level,
        msg="%s with code %s to '%s %s' in %s ms"
        % (
            msg_type,
            response.status_code,
            request.method,
            request.url,
            duration,
        ),
        extra={
            "request_json_fields": request_json_fields,
        },
        exc_info=exception_object,
    )


class LoggingMiddleware:
    """
    Logging middleware for processing requests and responses.
    """

    async def __call__(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
        *args,
        **kwargs,
    ) -> Response:
        start_time = time()
        exception_object = None
        request_body = await request.body()
        try:
            response = await call_next(request)
        except Exception as exc:
            response_body: bytes = bytes("Internal Server Error".encode())
            response = Response(
                content=response_body,
                status_code=500,
            )
            exception_object = exc
        else:
            chunks = []
            async for chunk in response.body_iterator:
                chunks.append(chunk)
            response_body = b"".join(chunks)

            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        if request.url.path in PASS_ROUTES:
            return response

        duration: int = ceil((time() - start_time) * 1000)
        task = BackgroundTask(
            func=log,
            req_body=request_body,
            res_body=response_body,
            request=request,
            response=response,
            duration=duration,
            exception_object=exception_object,
        )
        response.background = task

        return response
