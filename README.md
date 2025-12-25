# Json logger for FastAPI

I came across an interesting [article](https://habr.com/ru/articles/575454/) from 2021 on the Habr website about an asynchronous JSON logger.  
I decided to adapt the author's source code to fit my own needs and made several modifications.

In my project, I used QueueHandler — a log handler from the standard logging.handlers module that sends log records to a queue (queue.Queue, multiprocessing.Queue).  
QueueHandler provides several benefits:

- safe log handling in multi-threaded and multi-process environments;  
(FastAPI is often used with Uvicorn, which can run multiple worker processes. Standard log handlers like StreamHandler and FileHandler are not thread-safe, which can result in
log message interleaving, message loss, blocking issues.)

- improved performance;

- centralized log processing;  
(For example, logs can be written to a file, or sent to Elastic, Kafka, etc., using a single handler — without affecting the main application thread.)

Starting from Python 3.12, support for configuring the queue handler via configuration files or dictionaries was added.
However, for it to work correctly, you still need to call the .start() method on the logging.handlers.QueueListener.
The most straightforward way to do this in a FastAPI application is to call it inside the asynchronous lifespan function.


#### Core technologies
- FastAPI
- Pydantic 
- Uvicorn 
- Gunicorn

#### For testing:
- pytest
- pytest-mock
   
#### Requires Python 3.12+

### Example of logging http requests/responses:

```json
{
  "timestamp": "2025-05-30 16:18:23+03:00",
  "thread": 11954,
  "level": 20,
  "level_name": "information",
  "message": "Response with code 200 to 'POST http://0.0.0.0:8080/api/v1/public/user' in 2 ms",
  "source_log": "main",
  "app_name": "Json logger for FastAPI",
  "app_version": "1.0",
  "app_env": "dev",
  "duration": 2,
  "request": {
    "request_uri": "http://0.0.0.0:8080/api/v1/public/user",
    "request_referer": "http://0.0.0.0:8080/docs",
    "request_protocol": "HTTP/1.1",
    "request_method": "POST",
    "request_path": "/api/v1/public/user",
    "request_host": "127.0.0.1:8080",
    "request_size": 84,
    "request_content_type": "application/json",
    "request_headers": {
      "host": "0.0.0.0:8080",
      "connection": "keep-alive",
      "content-length": "84",
      "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
      "accept": "application/json",
      "content-type": "application/json",
      "origin": "http://0.0.0.0:8080",
      "referer": "http://0.0.0.0:8080/docs",
      "accept-encoding": "gzip, deflate",
      "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    },
    "request_body": "{\n  \"first_name\": \"string\",\n  \"last_name\": \"string\",\n  \"email\": \"****\"\n}",
    "request_direction": "in",
    "remote_ip": "127.0.0.1",
    "remote_port": 50296
  },
  "response": {
    "response_status_code": 200,
    "response_size": 71,
    "response_headers": {
      "content-length": "71",
      "content-type": "application/json"
    },
    "response_body": "{\"first_name\":\"string\",\"last_name\":\"string\",\"email\":\"****\"}"
  }
}
```

### Example log messages:
```json
{
  "timestamp": "2025-05-30 16:52:26+03:00",
  "thread": 11954,
  "level": 20,
  "level_name": "information",
  "message": "User data: first_name=string, last_name=string, email=****",
  "source_log": "api.api_v1.public.views",
  "app_name": "Asynchronous json logger for FastAPI",
  "app_version": "1.0",
  "app_env": "dev",
  "duration": 172
}
```

## How to run
clone repository:

```bash
git clone https://github.com/bizoxe/fastapi-json-logger.git
```
and navigate to cloned project

#### to run using uvicorn server:

```bash
cd fastapi-application
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 10
```

#### to run using gunicorn server:

```bash
cd fastapi-application
chmod +x ./run
./run
```

#### Command to run load testing:

```bash
# wrk must be installed on your Linux system
wrk -c200 -t1 -d15s http://0.0.0.0:8080/api/v1/public --timeout 15
```

