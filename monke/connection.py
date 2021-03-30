import socket
import pickle
import threading
from . import common
from . import server

from typing import Any

class Connection:
    def __init__(self, conn : socket.socket, addr : str, id : str = None, server : server.Server = None):
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
                data_len = self.conn.recv(64)

                if data_len:
                    data_len = int(data_len)

                    self.__handle_req(data_len)

            except ConnectionResetError:
                self.connected = False

        self.conn.close()
        self.server.connections.remove(self)
