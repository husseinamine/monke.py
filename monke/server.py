import socket
import threading
import pickle
import fuid
from . import common
from typing import Any

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

            conn = Connection(*req, self.fuid.fuid(), self)
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

class Connection:
    def __init__(self, conn : socket.socket, addr : str, id : str = None, server : Server = None):
        self.conn = conn
        self.addr = addr
        self.id = id
        self.server = server
        self.connected = True

    def __handle_req(self, data_len : int):
        req = self.conn.recv(data_len)
        req : common.Request = pickle.loads(req)

        for listener in self.server.listeners:
            if listener["event"] == req.event:
                threading.Thread(target=listener["func"], args=(self, req.data)).start()

        if req.event == '_SYSTEM':
            if req.data == 'disconnect':
                self.connected = False

    def emit(self, event : str, data : Any):
        if event != '_SYSTEM':
            req = common.Request()
            req.event = event
            req.data = data
            req = pickle.dumps(req)

            data_len = str(len(req)).encode('utf-8')
            data_len += b' ' * (64 - len(data_len))

            self.conn.sendall(data_len)
            self.conn.sendall(req)
        else:
            raise common.RestrictedEvent('_SYSTEM')

    def start(self):
        while self.connected:
            try:
                self.emit("ready", None)
                
                data_len = self.conn.recv(64)

                if data_len:
                    data_len = int(data_len)

                    self.__handle_req(data_len)

            except ConnectionResetError:
                self.connected = False

        self.conn.close()
        self.server.connections.remove(self)
