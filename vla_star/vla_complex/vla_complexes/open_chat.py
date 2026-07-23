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
from vla_star.vla_star import VLA_Star
class OpenChat(VLA_Complex):
    def __init__(self, extension: Text = Text()):
        super().__init__("openchat", True)
        print(f"[OpenChat]")

        ### Threads ###
        self.listening = False

        self.send_q = queue.Queue()
        self.inbound_q = queue.Queue()

        self.extension = extension

        self.local_agents = self.get_local_agents()
        names = [entry["name"] for entry in self.local_agents]
        self.agent_connection_info = {
            entry["name"]: {"host": entry["host"], "user": entry["user"]}
            for entry in self.local_agents
        }

        ### State ###
        self.state = State(session=[], impression=names)

    def get_local_agents(self):
        if type(self.extension) is Internet:
            # Be an activator
            pass
        if type(self.extension) is VLANet:
            # look up information on nearby agents from VLANet
            pass
        return [{"name": "Bob", "host": "127.0.0.1", "user": "olin"}]

    async def execute(self, name: str):
        """
        Open up a new conversation with another agent. This will end your current conversation.
        :param text: the name of the agent you want to converse with. (required)
        """
        chat = VLA_Star.get_activated_vla_star().get_chat_vla_complex()
        chat.interface.open_new_convo(name, self.agent_connection_info[name]["host"], self.agent_connection_info[name]["user"])
        chat.start_respond_thread()
        chat.state.impression["Chatting with"] = chat.interface.conversation.interlocutor
        chat.is_available = True
        return "Now send a message."