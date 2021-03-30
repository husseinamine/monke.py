import socket
import threading
import fuid
from . import connection

class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.listeners = []
        self.fuid = fuid.Generator()

    def __handler(self):
        self.server.listen()

        while True:
            req = self.server.accept()

            conn = connection.Connection(*req, self.fuid.fuid(), self)
            self.connections.append(conn)

            threading.Thread(target=conn.start)\
                .start()

    def on(self, event : str = None):
        def decorator(func):
            event_name = event

            if event_name == None:
                event_name = func.__name__
            
            self.listeners.append({
                "event": event_name,
                "func": func
            })

        return decorator

    def start(self, host : str = "127.0.0.1", port : int = 6000):
        self.server.bind((host, port))
        self.__handler()
