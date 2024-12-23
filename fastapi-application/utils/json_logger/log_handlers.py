"""
Log handlers.
"""

from logging.handlers import QueueHandler
import logging
from typing import override


class CustomQueueHandler(QueueHandler):
    """
    A subclass of QueueHandler.
    """

    @override
    def prepare(self, record: logging.LogRecord) -> logging.LogRecord:
        """
        The parent class prepare method sets by default the attributes record.exc_info,
        record.exc_text, record.args the value None.
        The values of these attributes are used later in the logging process.
        """
        record = super().prepare(record=record)

        record.exc_info = record.exc_info
        record.exc_text = record.exc_text
        record.args = record.args

        return record
