import socket
import json
import numpy as np
import struct
import os
import time
HOST = "127.0.0.1"

# Connect to Unity's server
def open_socket():
    PORT = os.environ.get("TERRAIN")
    if PORT is None:
        raise Exception("Cannot import terrain_fetcher before the PORT env variable is set.")
    else:
        PORT = int(PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    return sock



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
    sock = open_socket()
    msg = "getheightmap"
    sock.sendall(msg.encode('utf-8'))

    raw_len = recv_exact(sock, 4)
    (length,) = struct.unpack("<I", raw_len)

    json_bytes = recv_exact(sock, length)

    json_text = json_bytes.decode("utf-8")

    obj = json.loads(json_text)
    try:
        w, h = obj["width"], obj["height"]
        flat = obj["data"]

        data = np.array(flat).reshape((w, h))
    except KeyError:
        data = obj
    sock.close()
    return data

# Send the request
def get_destinations():
    sock = open_socket()
    msg = "getdestinations"
    sock.sendall(msg.encode('utf-8'))
    raw_len = recv_exact(sock, 4)
    (length,) = struct.unpack("<I", raw_len)
    json_bytes = recv_exact(sock, length)
    json_text = json_bytes.decode("utf-8")
    obj = json.loads(json_text)
    
    #print(obj)
    sock.close()
    return obj

def get_boat():
    sock = open_socket()
    msg = "getboat"
    sock.sendall(msg.encode('utf-8'))

    raw_len = recv_exact(sock, 4)
    (length,) = struct.unpack("<I", raw_len)

    json_bytes = recv_exact(sock, length)

    json_text = json_bytes.decode("utf-8")

    obj = json.loads(json_text)
    
    #print(obj)
    sock.close()
    return obj


if __name__ == "__main__":
    print(get_terrain())