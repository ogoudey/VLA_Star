import socket

HOST = "127.0.0.1"
PORT = 5000

# Connect to Unity's server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# Send the request
def get_terrain():
    msg = "getheightmap"
    sock.sendall(msg.encode('utf-8'))

    # Receive response (unknown size → read until closed)
    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk

    #sock.close()

    print("Received JSON length:", len(data))
    json_text = data.decode('utf-8')
    print("JSON sample:", json_text[:200])
    return json_text