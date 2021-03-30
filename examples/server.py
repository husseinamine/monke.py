import monke

s = monke.server.Server()

@s.on()
def questianne(conn, data):
    print(data)
    conn.emit("how_are_you", "how are you?")

@s.on("fine_u")
def _fine_u_handler(conn, data):
    print(data)
    conn.emit("fine_too", "im fine too")

s.start()