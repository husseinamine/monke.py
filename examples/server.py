from monke.server import Server

server = Server("127.0.0.1", 5556)

def on_data(addr, socket):
    print(addr, socket.response.data)
    socket.emit('hello-back', 'nob')

server.on('hello', on_data)