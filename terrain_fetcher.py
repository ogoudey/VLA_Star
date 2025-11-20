import socket
import json
import numpy as np
import struct

HOST = "127.0.0.1"
PORT = 5000

# Connect to Unity's server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))



def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise RuntimeError("Socket closed before receiving expected bytes")
        data += chunk
    return data

# Send the request
def get_terrain():
    msg = "getheightmap"
    sock.sendall(msg.encode('utf-8'))

    raw_len = recv_exact(sock, 4)
    (length,) = struct.unpack("<I", raw_len)

    json_bytes = recv_exact(sock, length)

    json_text = json_bytes.decode("utf-8")

    obj = json.loads(json_text)
    w, h = obj["width"], obj["height"]
    flat = obj["data"]

    arr = np.array(flat).reshape((w, h))

    return arr