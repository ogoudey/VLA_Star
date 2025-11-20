import socket
import struct
import numpy as np
import cv2
import threading
import base64


data_url = None
_lock = threading.Lock()

HOST = "127.0.0.1"
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print("Waiting for Unity camera connection...")
conn, addr = s.accept()
print("Connected:", addr)

def recv_exact(n):
    data = b""
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def receive_frames():
    
    print("Receiving frames in parallel thread...")
    while True:
        # Read 4-byte length
        length_bytes = recv_exact(4)
        if not length_bytes:
            break
        frame_len = struct.unpack("<I", length_bytes)[0]

        # Read compressed PNG frame
        frame_bytes = recv_exact(frame_len)
        if frame_bytes is None:
            break

        # Convert PNG → numpy → BGR for cv2
        img_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        set_latest(frame)
        cv2.imshow("Camera Stream", frame)
        if cv2.waitKey(1) == 27:  # ESC to quit
            break
    conn.close()
    cv2.destroyAllWindows()

def frame_to_data_url(frame):
    # Encode to PNG in memory
    success, encoded = cv2.imencode(".png", frame)
    if not success:
        raise ValueError("Failed to encode frame")

    # Convert to base64 string
    b64_bytes = base64.b64encode(encoded.tobytes())
    b64_string = b64_bytes.decode("utf-8")

    # Create data URL
    return f"data:image/png;base64,{b64_string}"

def set_latest(frame):
    global data_url
    with _lock:
        data_url = frame_to_data_url(frame)

def get_latest():
    with _lock:
        return data_url

    


threading.Thread(target=receive_frames, daemon=True).start()



