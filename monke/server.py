import socket
import threading
import pickle
import uuid
from . import structs

class Server:
    def __init__(self, host, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()

        self.server = server
        self.conns = []

    def on(self, event, callback):   
        connection = threading.Thread(target=self._acceptConn, args=(event, callback))
        connection.start()
        
    def _acceptConn(self, event, callback):
        while True:
            id = str(uuid.uuid4())
            conn, addr = self.server.accept()

            self.conns.append({'object': conn, 'id': id})

            connection = threading.Thread(target=self._handleConn, args=(conn, addr, event, callback, id))
            connection.start()

    def _handleConn(self, conn, addr, event, callback, id):
        connected = True

        while connected:
            data_len = conn.recv(64).decode('utf-8')
            
            if data_len:
                data_len = int(data_len)
                response = conn.recv(data_len)
                response = pickle.loads(response)

                if response.event == 'system' and response.data == '!disconnect':
                    connected = False

                if response.event == event:
                    socket = structs.Socket()
                    
                    socket.response = response
                    socket.emit = lambda event, data, force=False: self._emit(id, event, data, force)

                    callback(addr, socket)
        
        conn.close()

    def _emit(self, id, event, data, force):
        for conn in self.conns:
            if conn['id'] == id:
                if event != 'system' and force == False:
                    resp_data = structs.Response()
                    resp_data.event = event 
                    resp_data.data = data
                    resp_data = pickle.dumps(resp_data)

                    data_len = str(len(resp_data)).encode('utf-8')
                    data_len += b' ' * (64 - len(data_len))

                    conn['object'].sendall(data_len)
                    conn['object'].sendall(resp_data)
                else:
                    print('cant use event name \'system\' its reserved, use argument force=True if u want to use it')

