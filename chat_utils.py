import queue
import socket

def recv_line(sock: socket.socket):
    buffer = b""
    while not buffer.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            return None
        buffer += chunk
    return buffer.decode().strip()

def recv_loop(sock: socket.socket, inbound_q: queue.Queue, stop_event):
    try:
        while not stop_event.is_set():
            msg = recv_line(sock)
            if msg is None:
                break
            inbound_q.put(msg)
    except (ConnectionResetError, OSError):
        pass
    finally:
        stop_event.set()
        print("recv_loop exiting")

def send_loop(sock: socket.socket, send_q: queue.Queue, stop_event):
    try:
        while not stop_event.is_set():
            msg = send_q.get()
            sock.sendall((msg + "\n").encode())
    except (BrokenPipeError, ConnectionResetError, OSError):
        pass
    finally:
        stop_event.set()
        print("send_loop exiting")