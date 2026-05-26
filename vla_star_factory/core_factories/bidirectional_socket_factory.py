import queue
import socket
import threading
import time
from ...vla_star_factory.core_factories.utilities import socket_utilities
from typing import Callable

from vla_complex.vla_complexes.chat import Chat

class BiDirectionalSocket:
    def __init__(self, chat_port: int):
        self.chat_port = chat_port
        self.send_q = queue.Queue()
        self.inbound_q = queue.Queue()
        
        self.listening = False

        self.chat_vla_complex: Chat = None # this is bad design

    def run_server(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", self.chat_port))
            server.listen()
            self.listening = True
        except Exception as e:
            print(f"Failed to start chat server: {e}. Killing and trying again...")
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", self.chat_port))
            server.listen()
            self.listening = True
        print(f"Chat server waiting on port {self.chat_port}...")
        while self.listening:
            client_sock, addr = server.accept()
            print("Client connected:", addr)
            threading.Thread(
                target=self.handle_client,
                args=(client_sock,),
                daemon=True
            ).start()
    
    def handle_client(self, sock):
        stop_event = threading.Event()

        threading.Thread(
            target=socket_utilities.recv_loop,
            args=(sock, self.inbound_q, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=socket_utilities.send_loop,
            args=(sock, self.send_q, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=self.respond_loop,
            args=(stop_event,),
            daemon=True
        ).start()

        try:
            while not stop_event.is_set():
                time.sleep(1)
        finally:
            stop_event.set()
            sock.close()

    def respond_loop(self, stop_event):
        while not stop_event.is_set():
            msg = self.inbound_q.get()
            self.chat_vla_complex.respond(f"{msg}")
            self.chat_vla_complex.recede()

def build_bidirectional_socket(
        chat_port: int,
) -> BiDirectionalSocket:
    return BiDirectionalSocket(
        chat_port,
    )