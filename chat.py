import socket
import threading
import queue
import time
from chat_utils import recv_line, recv_loop, send_loop

def respond_loop(inbound_q, send_q, stop_event):
    try:
        while not stop_event.is_set():
            msg = inbound_q.get()
            print(f"\nRobot: {msg}\nReply: ")
            # do not send anything - sending is independent once again
    except Exception as e:
        print(f"Error in respond loop!: {e}")

def reply_loop(send_q, stop_event):
    try:
        while not stop_event.is_set():
            reply = input("\nReply: ")
            send_q.put(reply)
    except Exception as e:
        print(f"Error in respond loop!: {e}")
    

def run_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 5001))

    stop_event = threading.Event()
    inbound_q = queue.Queue()
    send_q = queue.Queue()

    threading.Thread(
        target=recv_loop,
        args=(sock, inbound_q, stop_event),
        daemon=True
    ).start()

    threading.Thread(
        target=send_loop,
        args=(sock, send_q, stop_event),
        daemon=True
    ).start()

    threading.Thread(
        target=respond_loop,
        args=(inbound_q, send_q, stop_event),
        daemon=True
    ).start()
    
    threading.Thread(
        target=reply_loop,
        args=(send_q, stop_event),
        daemon=True
    ).start()
    

    
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
        run_client()
    except OSError:
        print("Failed to run client. Make sure a Chat is beginning to listen/listening.")