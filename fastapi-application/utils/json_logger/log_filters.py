"""
This module contains log filters.
"""

import copy
import logging
import re
from collections.abc import (
    Mapping,
    Sequence,
)
from typing import override

from core.config import settings


class SensitiveDataFilter(logging.Filter):
    """
    Logs containing confidential information are filtered.
    """

    ignore_keys = {
        "name",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "process",
        "processName",
    }

    def __init__(
        self,
        mask_patterns: Sequence[str | re.Pattern[str]] = settings.log_cfg.regex_patterns,
        mask: str = settings.log_cfg.mask,
        mask_keys: Sequence[str] = settings.log_cfg.sensitive_keys,
    ) -> None:
        super(SensitiveDataFilter, self).__init__()
        self._mask_patterns = mask_patterns
        self._mask = mask
        self._mask_keys = set(mask_keys or {})

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        d = vars(record)
        for k, content in d.items():
            if k not in self.ignore_keys:
                d[k] = self.redact(content, k)

        return True

    def redact(self, content, key=None):
        try:
            content_copy = copy.deepcopy(content)
        except Exception:
            return content
        if content_copy:
            if isinstance(content_copy, Mapping):
                content_copy = type(content_copy)(
                    [(k, self._mask if k in self._mask_keys else self.redact(v)) for k, v in content_copy.items()]
                )

            elif isinstance(content_copy, list):
                content_copy = [self.redact(value) for value in content_copy]

            elif isinstance(content_copy, tuple):
                content_copy = tuple(self.redact(value) for value in content_copy)

            elif key and key in self._mask_keys:
                content_copy = self._mask

            elif isinstance(content_copy, str):
                for pattern in self._mask_patterns:
                    content_copy = re.sub(pattern, self._mask, content_copy)

        return content_copy


class NonErrorFilter(logging.Filter):
    """
    DEBUG and INFO level messages are logged.
    """

    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.INFO
