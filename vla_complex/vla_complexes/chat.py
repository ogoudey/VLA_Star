import threading
from typing import Optional
from ..vla_complex import VLA_Complex
from ..vla_complex_state import State
from ..general_dataset import SubDataset
from utilities.displays import timestamp
import time
import os

class Chat(VLA_Complex):
    recorded: bool
    dataset: Optional[SubDataset] = None
    
    def __init__(self, chat_port=5001, recorded=False, extension=None):
        super().__init__("chat", True)
        print(f"[Chat] Creating chat port on {chat_port}.")
        self.chat_port = chat_port
        self.recorded = recorded
        ### State ###
        self.state = State(session=[], impression={})

        ### Threads ###
        self.listening = False

        self.send_q = queue.Queue()
        self.inbound_q = queue.Queue()

        self.extension = extension

        if self.dataset is None:
            self.dataset = SubDataset("Chat", "user")

    def _repr__(self):
        return f"Chat repr"

    def __str__(self):
        return f"{self.tool_name}"

    def __getstate__(self):
        # For pickle
        state = self.__dict__.copy()
        del state['send_q']
        del state['inbound_q']
        self.listening = False
        return state

    def __setstate__(self, state):
        # For pickle
        self.__dict__.update(state)
        self.send_q = queue.Queue()
        self.inbound_q = queue.Queue()
        self.listening = False

    async def execute(self, text: str):
        """
        Say something directly to user. Use this for informal realistic conversation. Be as realistic as you can, no monologues/paragraphs.
        :param text: the message content. Fill this arg with all the content you want to send. (required)
        """
        if not self.listening:
            threading.Thread(target=self.run_server, daemon=True).start()
        await super().execute(text)
        self.reply(text)
        self.state.add_to_session("self", text)
        return "Message sent. Return immediately."

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
        #print(f"Chat server waiting on port {self.chat_port}...")
        while self.listening:
            client_sock, addr = server.accept()
            print(f"[Chat] Client connected: {addr}")
            threading.Thread(
                target=self.handle_client,
                args=(client_sock,),
                daemon=True
            ).start()

    def handle_client(self, sock):
        stop_event = threading.Event()

        threading.Thread(
            target=chat_utilities.recv_loop,
            args=(sock, self.inbound_q, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=chat_utilities.send_loop,
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
            self.respond(f"{msg}")
            self.recede()

    def recede(self):
        """
        Shoudl address any changes needed after rerun-request
        """  
        pass     

    def restore(self):
        """
        Should address the change in state after sending a context
        """
        if "Current user message" in self.state.impression:
            self.state.add_to_session("User message", self.state.impression["Current user message"])
            self.state.impression = {} # isnt working as intended

    def respond(self, user_input):
        #print(f"Message {user_input} received...")
        if self.recorded:
            if self.dataset is None:
                self.dataset = SubDataset("dialogue", "user")
            self.dataset.add_data({"user": [{"content": user_input, "timestamp": timestamp()}]})
        self.state.impression = {"Current user message":f"{user_input}"}
        self.rerun_agent()

    async def start(self):
<<<<<<< HEAD
        if not self.core.listening:
            threading.Thread(target=self.core.run_server, daemon=True).start()
=======
        print(f"[Chat] started listening on {self.chat_port}...")
        if not self.listening:
            threading.Thread(target=self.run_server, daemon=True).start()
>>>>>>> fd009e7f52284762929549267fa6505f5343703c
        if False: # NotImplemented
            global agent_name
            introduction.introduction_pipeline(rerun=runner, introduction_type=os.environ.get("INTRODUCTION_DATA", "None"), name=agent_name)
        else:
            self.reply("")

    def reply(self, message: str):
        if self.recorded:
            self.dataset.add_data({"robot": [{"content": message, "timestamp": timestamp()}]})
        self.core.send_q.put(message)