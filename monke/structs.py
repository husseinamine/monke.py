from typing import Any

class Response:
    event: str
    data: Any

class Socket:
    response: Response
    emit: Any