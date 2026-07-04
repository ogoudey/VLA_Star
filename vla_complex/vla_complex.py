from vla_complex.vlm import VLM
import time
from typing import List, Any, Callable

import os
from datetime import datetime
import threading
import asyncio
import socket
from utilities.displays import log, timestamp, update_activity
import queue
from .vla_complex_state import State

from abc import abstractmethod

runner: Callable = None
agent_name: str = None

class VLA_Complex:
    """
    Base class for all VLA_Complexes
    """
    tool_name: str
    def __init__(self, tool_name: str, on_start=False):
       
        
        self.tool_name = tool_name
        self.on_start = on_start
        
        self.use_frequency = 0.0

        self.state = State()

    @abstractmethod
    async def execute(self, *args, **kwargs):
        raise NotImplementedError()

    def rerun_agent(self):
        global runner
        if runner:
            runner(str(self))
        else:
            raise Exception("Why is there no runner function?")
        
    def agent_sleep(self):
        global runner
        runner("STOP")