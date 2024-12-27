"""
Logging schemas.
"""

import logging
from datetime import datetime
from typing import Union

from pydantic import (
    BaseModel,
    field_validator,
)

logger = logging.getLogger(__name__)


def decode_body(field: bytes, msg: str) -> str:
    try:
        decoded = field.decode()
        return decoded
    except UnicodeDecodeError:
        logger.exception(msg=msg, exc_info=True)

    return ""


class JsonLogBase(BaseModel):
    """
    Basic log schema.
    """

    timestamp: datetime
    thread: int
    level: int
    level_name: str
    message: str
    source_log: str
    app_name: str
    app_version: str
    app_env: str
    duration: int
    exceptions: Union[list[str] | str, None] = None


class RequestSideSchema(BaseModel):
    request_uri: str
    request_referer: str
    request_protocol: str
    request_method: str
    request_path: str
    request_host: str
    request_size: int
    request_content_type: str
    request_headers: dict
    request_body: str
    request_direction: str
    remote_ip: str
    remote_port: int

    @field_validator(
        "request_body",
        mode="before",
    )
    @classmethod
    def validate_body(cls, field: bytes) -> str:
        exc_msg = "Failed to decode the request body"
        req_body = decode_body(field=field, msg=exc_msg)

        return req_body


class ResponseSideSchema(BaseModel):
    response_status_code: int
    response_size: int
    response_headers: dict
    response_body: str

    @field_validator(
        "response_body",
        mode="before",
    )
    @classmethod
    def validate_body(cls, field: bytes) -> str:
        exc_msg = "Failed to decode the response body"
        resp_body = decode_body(field=field, msg=exc_msg)

        return resp_body


class RequestJsonLog(BaseModel):
    """
    Log request-response schema.
    """

    request: RequestSideSchema
    response: ResponseSideSchema
    duration: int
