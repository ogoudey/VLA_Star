import threading
from typing import Optional
from ..vla_complex import VLA_Complex
from ..vla_complex_state import State
from ..general_dataset import SubDataset
from utilities.displays import timestamp
import time
import os

class Chat(VLA_Complex):
    dataset: Optional[SubDataset] = None # should be in superclass, typed to self

    def __init__(self, bidirectional_socket, tool_name, description, return_value, on_start, monitors, recorded):
        super().__init__(tool_name, description, return_value, on_start, monitors, recorded)
        self.core = bidirectional_socket
        self.core.chat_vla_complex = self
        ### State ###
        self.state = State(session=[], impression={})

    async def execute(self, text: str):
        if not self.core.listening:
            threading.Thread(target=self.core.run_server, daemon=True).start()
        self.reply(text)
        self.state.add_to_session("self", text)
        return self.return_value

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
        print(f"Message {user_input} received...")
        if self.recorded:
            if self.dataset is None:
                self.dataset = SubDataset("dialogue", "user")
            self.dataset.add_data({"user": [{"content": user_input, "timestamp": timestamp()}]})
        self.state.impression = {"Current user message":f"{user_input}"}
        self.rerun_agent()

    async def start(self):
        if not self.core.listening:
            threading.Thread(target=self.core.run_server, daemon=True).start()
        if False: # NotImplemented
            global agent_name
            introduction.introduction_pipeline(rerun=runner, introduction_type=os.environ.get("INTRODUCTION_DATA", "None"), name=agent_name)
        else:
            self.reply("")

    def reply(self, message: str):
        if self.recorded:
            if self.dataset is None:
                self.dataset = SubDataset("dialogue", "user")
            self.dataset.add_data({"robot": [{"content": message, "timestamp": timestamp()}]})
        self.core.send_q.put(message)