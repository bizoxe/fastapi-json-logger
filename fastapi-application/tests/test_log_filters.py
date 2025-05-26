import json
import logging
import sys
from logging.handlers import RotatingFileHandler

import pytest

from utils.json_logger.json_log_formatter import JSONLogFormatter
from utils.json_logger.log_filters import (
    NonErrorFilter,
    SensitiveDataFilter,
)

regex = (
    r"\d{3}-\d{2}-\d{4}",
    r"\d{4}-\d{4}-\d{4}-\d{4}",
    r"(password|token|secret)\s*=\s*([^\s]+)",
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
)
keys = (
    "headers",
    "token",
    "password",
    "api_key",
)


@pytest.fixture
def setup_logger(request):
    def _logger(_handler, flag: bool = False):
        if flag:
            log = logging.getLogger(request.node.name)
        else:
            log = logging.getLogger(__name__)

        log.setLevel(level=logging.DEBUG)
        log.addHandler(_handler)
        return log

    return _logger


@pytest.fixture
def console_output(setup_logger):
    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(JSONLogFormatter())
    console.addFilter(SensitiveDataFilter(mask_patterns=regex, mask_keys=keys, mask="REDACTED"))

    return setup_logger(console, flag=True)


@pytest.fixture
def rotating_file_output(get_log_dir, setup_logger):
    get_log_dir.mkdir(exist_ok=True)
    file_name = get_log_dir / "test_non_error.jsonl"
    file_handler = RotatingFileHandler(filename=file_name, mode="a")
    file_handler.setLevel(level=logging.DEBUG)
    file_handler.setFormatter(JSONLogFormatter())
    file_handler.addFilter(NonErrorFilter())

    yield setup_logger(file_handler)

    for item in get_log_dir.iterdir():
        if item.is_file():
            item.unlink()
    get_log_dir.rmdir()


@pytest.mark.parametrize(
    "original, masked",
    [
        (
            "John [513-84-7329] made a payment with credit card 1234-5678-9012-3456.",
            "John [REDACTED] made a payment with credit card REDACTED.",
        ),
        (
            "User token=tokenvalue",
            "User REDACTED",
        ),
        ("User password=secretpassword", "User REDACTED"),
        ("User e-mail: dolgorukaya@gmail.com", "User e-mail: REDACTED"),
    ],
)
def test_sensitive_data_filter_msg_string(
    original,
    masked,
    caplog,
    console_output,
) -> None:
    console_output.info(original)
    assert caplog.records[0].message == masked

    caplog.clear()
    console_output.info("%s" % (original,))
    assert caplog.records[0].message == masked


def test_sensitive_data_filter_args(
    caplog,
    console_output,
) -> None:
    console_output.info(
        "Request %(headers)s and user %(password)s",
        {"headers": {"Authorization": "Bearer tokenvalue"}, "password": "secretpwd"},
    )
    assert caplog.records[0].message == "Request REDACTED and user REDACTED"

    caplog.clear()
    console_output.info("Used %(api_key)s and %(token)s", {"api_key": "value", "token": "value"})
    assert caplog.records[0].message == "Used REDACTED and REDACTED"

    caplog.clear()
    test_case = {"api_key": "value", "password": "xyz"}
    test_case_masked = {"api_key": "REDACTED", "password": "REDACTED"}
    console_output.info("Used multi args %s %s", test_case, test_case)
    assert caplog.records[0].message == f"Used multi args {dict(test_case_masked)} {dict(test_case_masked)}"


def test_non_error_filter(
    rotating_file_output,
    get_log_dir,
) -> None:
    rotating_file_output.debug("Debug message")
    rotating_file_output.info("Info message")
    rotating_file_output.warning("Warning message")
    rotating_file_output.error("Error message")
    rotating_file_output.critical("Critical message")
    file = get_log_dir / "test_non_error.jsonl"
    log_entries = [json.loads(line) for line in file.read_text().splitlines()]
    assert len(log_entries) == 2
    debug_msg = log_entries[0]
    info_msg = log_entries[1]
    assert debug_msg["source_log"] == logging.getLogger(__name__).name
    assert debug_msg["message"] == "Debug message"
    assert debug_msg["level"] == logging.DEBUG

    assert info_msg["source_log"] == logging.getLogger(__name__).name
    assert info_msg["message"] == "Info message"
    assert info_msg["level"] == logging.INFO
