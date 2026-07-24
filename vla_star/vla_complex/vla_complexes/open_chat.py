import threading
from typing import Optional, List
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
from vla_star.vla_complex.utilities.chat_core import SecretManager, LocalNetworkManager
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

        ### State ###
        self.state = State(session=[], impression=self.local_agents)

    def get_local_agents(self) -> List[str]:
        if type(self.extension) is Internet:
            return LocalNetworkManager.get_local_agents()
            pass
        if type(self.extension) is VLANet:
            # look up information on nearby agents from VLANet
            pass
        return []
        
    async def execute(self, name: str):
        """
        Open up a new conversation with another agent. This will end your current conversation.
        :param text: the name of the agent you want to converse with. (required)
        """
        chat = VLA_Star.get_activated_vla_star().get_chat_vla_complex()
        user, host = LocalNetworkManager.get_host_and_user_of_name(name)
        chat.interface.open_new_convo(name, host, user)
        chat.start_respond_thread()
        chat.state.impression["Chatting with"] = chat.interface.conversation.interlocutor
        chat.is_available = True
        return "Now send a message."