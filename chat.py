import socket


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Connecting...")
s.connect(("127.0.0.1", 5001))
print("Connected!")

intro = "From client"
s.sendall(intro.encode("utf-8"))

buffer = b""
print("Waiting for initiation...")
while not buffer.endswith(b"\n"):
    chunk = s.recv(1)
    if not chunk:
        break
    buffer += chunk
print(buffer.decode().strip())
try:
    while True:
        msg = input("Input: ")
        # send
        s.sendall(msg.encode("utf-8"))

        buffer = b""
        while not buffer.endswith(b"\n"):
            chunk = s.recv(1)
            if not chunk:
                break
            buffer += chunk
        print("Response:", buffer.decode().strip())
except KeyboardInterrupt:
    s.close() 