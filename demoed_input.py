import socket
import threading
import queue
import time
from typing import List
from chat_utils import recv_line, recv_loop, send_loop
import os
import inspect

class VLA_ComplexStripped:
    tool_name: str
    signature: dict[str, str]

class ChoiceData:
    context: dict # just visual
    vla_complexes: List[VLA_ComplexStripped]

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

def respond_loop(inbound_q, send_q, stop_event):
    try:
        while not stop_event.is_set():
            context, stripped_vla_complexes = inbound_q.get()
            print(f"{context}")
            while True:
                for vla_complex in stripped_vla_complexes:
                    print(f"____{vla_complex.tool_name}____")
                    print(f"{vla_complex.signature}")
                    choice = input(f"(\"\" to skip): ")
                    if not choice == "":
                        args = {}
                        for arg_name, type in vla_complex.signature.items():
                            args[arg_name] = input(f"\t{arg_name}: ")
                        send_q.put(tool_name, args)
                    else:
                        print(f"_______")
                print(f"\nV V V V V\n")
    except Exception as e:
        print(f"Error in respond loop!: {e}")

    

def choice_loop(send_q, stop_event):
    try:
        while not stop_event.is_set():
            reply = args
            send_q.put(reply)
    except Exception as e:
        print(f"Error in respond loop!: {e}")

def connect(chat_port):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", chat_port))
            return sock
        except ConnectionRefusedError:
            print("Waiting...", end="\r")
            time.sleep(1)

def run_client(chat_port=5001):
    sock = connect(chat_port)
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
        print("Disconnected. You may close this chat terminal.")
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
        print("Failed to run client. Make sure a Chat is beginning to listen/listening.")
