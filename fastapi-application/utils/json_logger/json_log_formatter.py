"""
This module contains a custom JSON formatter for logging.
"""

import json
import logging
import traceback
from datetime import datetime
from typing import override

from core.config import settings
from utils.json_logger.schemas import JsonLogBase

LOG_LEVELS: dict[int, str] = {
    logging.CRITICAL: "CRITICAL",
    logging.ERROR: "ERROR",
    logging.WARNING: "WARNING",
    logging.INFO: "information",
    logging.DEBUG: "debug",
    logging.NOTSET: "trace",
}


class JSONLogFormatter(logging.Formatter):
    """
    Class-formatter for logs in json format.
    """

    @override
    def format(self, record: logging.LogRecord) -> str:
        """
        Converts a log object to json.
        Args:
            record: Log object.

        Returns:
                Log string in JSON format.
        """
        log_object: dict = self._format_log_object(record)
        return json.dumps(log_object, default=str)

    @staticmethod
    def _format_log_object(record: logging.LogRecord) -> dict:
        """
        Generates fields for logging.
        Args:
            record: Log record.

        Returns:
                Dictionary with log objects.
        """
        now = datetime.fromtimestamp(record.created).astimezone().replace(microsecond=0)
        message = record.getMessage()
        duration = record.duration if hasattr(record, "duration") else record.msecs
        json_log_fields = JsonLogBase(
            timestamp=now,
            thread=record.process,
            level=record.levelno,
            level_name=LOG_LEVELS[record.levelno],
            message=message,
            source_log=record.name,
            duration=duration,
            app_name=settings.api.name,
            app_version=settings.api.version,
            app_env=settings.api.environment,
        )

        if record.exc_info:
            json_log_fields.exceptions = traceback.format_exception(*record.exc_info)

        elif record.exc_text:
            json_log_fields.exceptions = record.exc_text

        json_log_obj = json_log_fields.model_dump(
            exclude_unset=True,
        )

        if hasattr(record, "request_json_fields"):
            json_log_obj.update(record.request_json_fields)

        return json_log_obj
