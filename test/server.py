import socket

ip = socket.gethostbyname(socket.gethostname())

# asker side
s1 = socket.socket()
s1.bind((socket.gethostbyname(socket.gethostname()), 12397))
s1.listen(19)
conn, addr = s1.accept()
conn.send(json.dumps(tx.serialize()))
signature = conn.recv(5000)
