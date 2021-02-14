from monke.client import Client

client = Client("127.0.0.1", 5556)

client.emit('hello', 'how are you!')

def handle(socket):
    print(socket.response.data, socket.response.event)

client.on('hello-back', handle)

#client.disconnect()