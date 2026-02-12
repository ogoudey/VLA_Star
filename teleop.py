import socket
import threading
import time
import queue
import os

try:
    if ("DISPLAY" not in os.environ) and ("linux" in sys.platform):
        raise ImportError("pynput blocked intentionally due to no display.")
    from pynput import keyboard
except ImportError:
    keyboard = None
    PYNPUT_AVAILABLE = False
except Exception as e:
    keyboard = None
    PYNPUT_AVAILABLE = False

def send_loop(sock: socket.socket, send_q: queue.Queue, stop_event):
    try:
        while not stop_event.is_set():
            tuple = send_q.get()
            msg0 = f"{tuple[0]}"
            msg1 = f"{1}" if tuple[1] else f"{0}"
            msg = msg0 + msg1
            sock.sendall(msg.encode())
    except (BrokenPipeError, ConnectionResetError, OSError):
        pass
    finally:
        stop_event.set()
        print("send_loop exiting")

def recv_line(sock: socket.socket):
    buffer = b""
    while not buffer.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            return None
        buffer += chunk
    return buffer.decode().strip()

def recv_loop(sock: socket.socket, stop_event):
    try:
        while not stop_event.is_set():
            msg = recv_line(sock)
            if msg is None:
                break
            print(f"Prompt: {msg}")
    except (ConnectionResetError, OSError):
        pass
    finally:
        stop_event.set()


def run_client(teleop_port=5008):
    print(f"Opened teleop client on {teleop_port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", teleop_port))

    stop_event = threading.Event()
    send_q = queue.Queue()

    def on_press(key):
        try:
            k = getattr(key, "char", None)
            if k:
                send_q.put((k.lower(), True))
        except Exception as e:
            print("Press error:", e)

    def on_release(key):
        try:
            k = getattr(key, "char", None)
            if k:
                send_q.put((k.lower(), False))
        except Exception as e:
            print("Press error:", e)
    threading.Thread(
        target=send_loop,
        args=(sock, send_q, stop_event),
        daemon=True
    ).start()
    
    threading.Thread(
        target=recv_loop,
        args=(sock, stop_event),
        daemon=True
    ).start()

    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release, # but I need to pass _on_press and _on_release the send_q
        suppress=False
    )

    keyboard_listener.start()
    keyboard_listener.wait()
    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        sock.close()

if __name__ == "__main__":
    try:
        import sys
        if len(sys.argv) > 1:
            run_client(int(sys.argv[1]))
        else:
            run_client()
    except OSError:
        print("Failed to run client. Make sure a VLA_Complex with a keyboard teleop is beginning to listen/listening.")