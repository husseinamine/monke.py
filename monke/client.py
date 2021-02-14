import pickle
import socket
import threading
from . import structs

class Client:
    def __init__(self, host, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))

        self.disconnected = False
        self.client = client

    def emit(self, event, data, force=False):
        if event != 'system' and force == False:
            resp_data = structs.Response()
            resp_data.event = event 
            resp_data.data = data
            resp_data = pickle.dumps(resp_data)

            data_len = str(len(resp_data)).encode('utf-8')
            data_len += b' ' * (64 - len(data_len))

            self.client.sendall(data_len)
            self.client.sendall(resp_data)
        else:
            print('cant use event name \'system\' its reserved, use argument force=True if u want to use it')

    def on(self, event, callback):
        if not self.disconnected:   
            listener = threading.Thread(target=self._handleConn, args=(event, callback))
            listener.start()

    def _handleConn(self, event, callback):
        connected = True

        while connected:
            data_len = self.client.recv(64).decode('utf-8')
            
            if data_len:
                data_len = int(data_len)
                response = self.client.recv(data_len)
                response = pickle.loads(response)

                if response.event == 'system' and response.data == '!disconnect':
                    connected = False

                if response.event == event:
                    socket = structs.Socket()
                    
                    socket.response = response
                    socket.emit = self.emit

                    callback(socket)

        self.client.close()


    def disconnect(self):
        self.disconnected = True
        
        resp_data = structs.Response()
        resp_data.event = 'system'
        resp_data.data = '!disconnect'
        resp_data = pickle.dumps(resp_data)

        data_len = str(len(resp_data)).encode('utf-8')
        data_len += b' ' * (64 - len(data_len))

        self.client.sendall(data_len)
        self.client.sendall(resp_data)

        self.client.close()