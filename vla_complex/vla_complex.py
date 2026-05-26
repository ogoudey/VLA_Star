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
    description: str
    return_value: str
    on_start: bool
    monitors: List
    recorded: bool

    def __init__(self, tool_name: str, description: str, return_value: str, on_start: bool, monitors: List, recorded: bool):        
        self.tool_name = tool_name
        self.description = description
        self.return_value = return_value
        self.on_start = on_start
        self.monitors = monitors
        self.recorded = recorded
        
        self.use_frequency = 0.0

        self.execute.__doc__ = description

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