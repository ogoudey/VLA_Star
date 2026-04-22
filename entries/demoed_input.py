import socket
import threading
import queue
import time
from typing import List
import os
import inspect
from dataclasses import dataclass, asdict
import json
"""
Script for making remote decisions - NOT DONE
"""
@dataclass
class VLA_ComplexStripped:
    tool_name: str
    signature: dict[str, str]

@dataclass
class ChoiceData:
    context: dict # just visual
    vla_complexes: List[VLA_ComplexStripped]
    def __init__(self, context=dict(), vla_complexes=[]):
        self.context = context
        self.vla_complexes = vla_complexes


def recv_object(sock: socket.socket):
    buffer = b""

    while b"\n" not in buffer:
        chunk = sock.recv(4096)
        if not chunk:
            return None
        buffer += chunk

    line, _, remainder = buffer.partition(b"\n")

    return json.loads(line.decode("utf-8"))

def recv_loop(sock: socket.socket, inbound_q: queue.Queue, stop_event):
    try:
        while not stop_event.is_set():
            data = recv_object(sock)
            if data is None:
                break

            # Reconstruct dataclasses
            vla_complexes = [
                VLA_ComplexStripped(**v)
                for v in data["vla_complexes"]
            ]

            choice_data = ChoiceData(
                context=data["context"],
                vla_complexes=vla_complexes
            )

            inbound_q.put(choice_data)
    except (ConnectionResetError, OSError):
        pass
    finally:
        stop_event.set()

def respond_loop(inbound_q, send_q, stop_event):
    try:
        while not stop_event.is_set():
            choice_data = inbound_q.get()
            print(f"{choice_data.context}")
            choosing = True
            while choosing:
                for vla_complex in choice_data.vla_complexes:
                    print(f"____{vla_complex.tool_name}____")
                    print(f"{vla_complex.signature}")
                    choice = input(f"(\"\" to skip): ")
                    if not choice == "":
                        choice = [vla_complex.tool_name]
                        for arg_name, type in vla_complex.signature.items():
                            choice.append(input(f"\t{arg_name}: "))
                        send_q.put(choice)
                        choosing = False
                        break
                    else:
                        print(f"_______")
                print(f"\nV V V V V\n")
    except Exception as e:
        print(f"Error in respond loop!: {e}")

def send_loop(sock: socket.socket, send_q: queue.Queue, stop_event):
        try:
            while not stop_event.is_set():
                choice = send_q.get()
                msg = json.dumps(choice)
                sock.sendall((msg + "\n").encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            stop_event.set()

def connect(chat_port):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("127.0.0.1", chat_port))
            return sock
        except ConnectionRefusedError:
            print("Waiting...", end="\r")
            time.sleep(1)

def run_client(input_port=5010):
    sock = connect(input_port)
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
    print(f"Demoed input client started.")
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
