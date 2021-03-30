from typing import Any

class Request:
    event: str
    data: Any

class RestrictedEvent(Exception):
    def __init__(self, event):
        message = "'%s' event name is restricted" % event
        super().__init__(message)
