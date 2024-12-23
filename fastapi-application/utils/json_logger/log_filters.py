"""
This module contains log filters.
"""

import logging
from typing import (
    override,
    Any,
)

from core.config import settings

PATTERNS = settings.log_cfg.patterns


class SensitiveDataFilter(logging.Filter):
    """
    Logs containing confidential information are filtered.
    """

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self.redact(record.msg)
        if isinstance(record.args, dict):
            for key in record.args.keys():
                if key in PATTERNS:
                    record.args[key] = "<<TOP SECRET!>>"

        if record.args:
            record.args = tuple(self.redact(arg) for arg in record.args)

        return True

    @staticmethod
    def redact(msg: str | Any) -> str | Any:
        if isinstance(msg, str):
            for pattern in PATTERNS:
                msg = msg.replace(pattern, "<<TOP SECRET!>>")

        return msg


class NonErrorFilter(logging.Filter):
    """
    DEBUG and INFO level messages are logged.
    """

    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.INFO
