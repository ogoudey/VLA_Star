
from vla import VLA
from vlm import VLM
import time
from typing import List, Any, Callable

import os
from datetime import datetime
import threading
import asyncio
import socket
from displays import log, timestamp, update_activity
import queue
import scheduler 

runner: Callable = None
agent_name: str = None

class VLA_Complex:
    """
    Base class for all modules, VLA_Complexes
    """

    tool_name: str
    def __init__(self, vla: Any, tool_name: str, on_start=False):
        self.vla = vla        
        
        self.tool_name = tool_name
        self.on_start = on_start
        self.use_frequency = 0.0

        self.name_in_session = tool_name
        self.name_in_impression = tool_name

    async def execute(self, instruction: str):
        """___________________________"""
        self.use_frequency += 1
        instruction_print = f"...{instruction[-30:]}" if len(instruction) > 20 else instruction

    def rerun_agent(self):
        global runner
        if runner:
            runner(str(self))
        else:
            raise Exception("Why is there no runner function?")
        
    def agent_sleep(self):
        global runner
        runner("STOP")