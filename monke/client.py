import socket
import threading
import pickle
from . import common

from typing import Any

class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listeners = []
        self.connected = True

    def __handle_req(self, data_len : int):
        req = self.client.recv(data_len)
        req : common.Request = pickle.loads(req)

        for listener in self.listeners:
            if listener["event"] == req.event:
                threading.Thread(target=listener["func"], args=(self, req.data)).start()


    def __handler(self):
        while self.connected:
            try:
                data_len = self.client.recv(64)

                if data_len:
                    data_len = int(data_len)

                    self.__handle_req(data_len)

            except ConnectionResetError:
                self.connected = False

        self.client.close()

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

    
    def emit(self, event : str, data : Any):
        if event != '_SYSTEM':
            req = common.Request()
            req.event = event
            req.data = data
            req = pickle.dumps(req)

            data_len = str(len(req)).encode('utf-8')
            data_len += b' ' * (64 - len(data_len))

            self.client.sendall(data_len)
            self.client.sendall(req)
        else:
            raise common.RestrictedEvent('_SYSTEM')

    def start(self, host : str = "127.0.0.1", port : int = 6000):
        self.client.connect((host, port))
        self.__handler()