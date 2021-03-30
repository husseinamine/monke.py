import monke

c = monke.client.Client()

@c.on()
def ready(conn, data):
    conn.emit("questianne", "why is why not why?")

@c.on("how_are_you")
def how_are_youez_handler(conn, data):
    print(data)
    conn.emit("fine_u", "fine how are you?")

@c.on()
def fine_too(conn, data):
    print(data)

c.start()