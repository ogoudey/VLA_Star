import threading
from typing import Optional
from ..vla_complex import VLA_Complex
from ..vla_complex_state import State
from ..general_dataset import SubDataset
from vla_star.utilities.displays import timestamp
import time
import os
import queue
import socket
import signal
from vla_star.utilities.extension import Text, VLANet, Internet

from vla_star.vla_complex.utilities.chat_core import OutInterface

class Chat(VLA_Complex):
    recorded: bool
    dataset: Optional[SubDataset] = None
    
    def __init__(self, recorded=False, extension: Text = Text()):
        super().__init__("chat", False)
        print(f"[Chat] Creating chat port.")

        self.recorded = recorded

        ### State ###
        self.state = State(session=[], impression={})

        self.extension = extension

        if self.dataset is None and recorded:
            self.dataset = SubDataset("Chat", "user")

        self.stop_conversation = threading.Event()
        self.conversing = False
        self.interface = OutInterface.open_interface()
        self.interface.router.on_router_conversation = self.start_respond_thread
        self.interface.router.stop_responding_bool = self.stop_conversation
        self.is_available = False

        

    def set_availability(self, value: bool):
        self.is_available = value

    def start_respond_thread(self):
        if self.conversing:
            print(f"[Chat] Already conversing. Not starting respond_loop")
            return
        else:
            print(f"[Chat] Creating respond_loop thread")
        self.is_available = True
        self.conversing = True
        t = threading.Thread(target=self.respond_loop, daemon=True)
        t.start()

    def _repr__(self):
        return f"Chat repr"

    def __str__(self):
        return f"{self.tool_name}"

    async def execute(self, text: str):
        """
        Say something directly to user. Use this for informal realistic conversation. Be as realistic as you can, no monologues/paragraphs.
        :param text: the message content. Fill this arg with all the content you want to send. (required)
        """
        print(f"[Chat] Sending \"{text}\"")
        try:
            self.interface.add_to_conversation(text)
            self.state.add_to_session(self.interface.conversation.interlocutor, text)
            return "Message sent. Return immediately."
        except Exception as e:
            return "Not in a conversation. Use `open_chat` to do this."

    def respond_loop(self):
        print(f"[Chat] starting respond loop...")
        while not self.stop_conversation.is_set(): # bit redundant maybe...
            msg = self.interface.conversation.inbound.get()
            print(f"[Chat] Received chat message {msg}.")
            if msg == "bye":
                print(f"[Chat] That's a signal to stop responding...")
                break
            self.respond(f"{msg}")
        self.is_available = False
        self.stop_conversation.clear()
        self.conversing = False
        print(f"[Chat] Exiting respond loop...")

    def respond(self, user_input):
        if self.recorded:
            if self.dataset is None:
                self.dataset = SubDataset("dialogue", "user")
            self.dataset.add_data({"user": [{"content": user_input, "timestamp": timestamp()}]})
        self.state.impression = {"Current user message":f"{user_input}"}
        self.rerun_agent()