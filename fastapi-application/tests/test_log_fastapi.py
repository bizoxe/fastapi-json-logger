import json
import logging

import pytest
from _pytest.logging import LogCaptureFixture
from fastapi.testclient import TestClient

from utils.json_logger.json_log_formatter import JSONLogFormatter

request_params = {
    "request_uri",
    "request_referer",
    "request_protocol",
    "request_method",
    "request_path",
    "request_host",
    "request_size",
    "request_content_type",
    "request_headers",
    "request_body",
    "request_direction",
    "remote_ip",
    "remote_port",
}

response_params = {
    "response_status_code",
    "response_size",
    "response_headers",
    "response_body",
}


def format_caplog_record(record: logging.LogRecord):
    return json.loads(JSONLogFormatter().format(record))


def test_log_middleware(
    client: TestClient,
    prepare_logging,
    caplog: LogCaptureFixture,
    disable_loggers_during_tests,
) -> None:
    logging.getLogger("test").propagate = True
    caplog.set_level(level=logging.INFO, logger="root")
    response = client.get("/")
    assert response.status_code == 200
    log_request_response = format_caplog_record(caplog.records[0])
    assert log_request_response["timestamp"] != ""
    assert log_request_response["level"] == 20
    assert log_request_response["message"].split()[0] == "Response"
    assert log_request_response["source_log"] == "test"
    request_log = log_request_response["request"]
    response_log = log_request_response["response"]
    all_req_params = all(map(lambda x: x in request_log, request_params))
    all_resp_params = all(map(lambda y: y in response_log, response_params))
    assert all_req_params is True
    assert all_resp_params is True
    assert request_log["request_method"] == "GET"
    assert request_log["request_path"] == "/"
    serialize_resp_body = json.loads(response_log["response_body"])
    assert serialize_resp_body == dict({"message": "Hello world from FastAPI app"})

    caplog.clear()
    response = client.get("/error")
    assert response.status_code == 500
    log_request_response = format_caplog_record(caplog.records[0])
    assert log_request_response["level"] == 40
    assert log_request_response["message"].split()[0] == "ERROR"
    assert log_request_response["source_log"] == "test"
    assert log_request_response["request"]["request_path"] == "/error"
    assert "exceptions" in log_request_response
    assert log_request_response["response"]["response_body"] == "Internal Server Error"
    logging.getLogger("test").propagate = False


@pytest.mark.parametrize(
    "level, levelno, message",
    [
        ("debug", 10, "Debug message"),
        ("info", 20, "Info message"),
        ("exception", 40, "An error occurred"),
        ("critical", 50, "Critical message"),
    ],
)
def test_log_routes(
    level: str,
    levelno: int,
    message: str,
    client: TestClient,
    caplog: LogCaptureFixture,
    disable_loggers_during_tests,
) -> None:
    caplog.clear()
    caplog.set_level(level=logging.DEBUG, logger="root")
    response = client.get(f"/levels/{level}")
    assert response.status_code == 200
    caplog_records = format_caplog_record(caplog.records[0])
    assert caplog_records["level"] == levelno
    assert caplog_records["source_log"] == "test_2"
    assert caplog_records["message"] == message
    if level == "exception":
        assert "exceptions" in caplog_records


def test_logs_written_to_file(
    get_log_dir,
    disable_loggers_during_tests,
    caplog: LogCaptureFixture,
    client: TestClient,
    prepare_logging,
) -> None:
    caplog.set_level(level=logging.INFO, logger="root")
    file = get_log_dir / "test_log.jsonl"
    caplog.clear()
    response = client.get("/public")
    log_entries = [json.loads(line) for line in file.read_text().splitlines()]
    assert len(log_entries) == 2
    assert log_entries[0]["source_log"] == "test_2"
    assert log_entries[0]["level"] == 20
    assert log_entries[0]["message"] == "User Elena and secretpwd"

    assert log_entries[1]["source_log"] == "test"
