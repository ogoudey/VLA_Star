from typing import List, Callable, Optional
import asyncio
import sys
import weakref
from vla_star.context_engine.context_engine import OrderedContextEngine,OrderedContextLLMEngine
from vla_star.vla_complex.vla_complex import VLA_Complex
import vla_star.vla_complex.vla_complex as vla_complex_module
from vla_star.context_engine.runner import ThinkingMachine
import os
from vla_star.utilities.extension import Extension
from vla_star.tool_choice_models.tool import Tool
from vla_star.vla_complex.vla_complexes.chat import Chat
class OneVLA_StarPerProcess(Exception):
    pass

class VLA_Star:
    """
    Central class representing the agent
    """
    name: str
    context_engine: OrderedContextEngine
    vla_complexes: List[VLA_Complex]

    _activated = weakref.WeakSet()

    def __init__(self,
        name: str,
        context_engine: OrderedContextEngine,
        tools: List[Tool],
        extension: Extension
    ):
        self.name = name
        self.context_engine = context_engine
        self.tools = tools
        self.extension = extension
        self.context_engine.attach_tools(self.tools)
        vla_complex_module.agent_name = self.name # idk why i need this

        if len(VLA_Star._activated) > 0:
            raise OneVLA_StarPerProcess("There is already a VLA_Star instantiated in this python process. :(")
        type(self)._activated.add(self)

    @classmethod
    def get_all_instances(cls):
        # Returns a standard list of the remaining live instances
        return list(cls._activated)
    
    @classmethod
    def get_activated_vla_star(cls) -> "VLA_Star":
        return VLA_Star.get_all_instances()[0]
        
    def safe_start(self):
        print(f"[VLA_Star] Safe start on process {os.getpid()}.")
        try:
            self.start()
        except KeyboardInterrupt as k:
            print("[VLA_Star] Safe start receives KeyboardInterrupt.")
            pass

    def start(self, prompt: str | None = None):
        vlacs_to_start = []
        for tool in self.tools:
            if hasattr(tool.vla_complex, "start") and tool.vla_complex.on_start:
                vlacs_to_start.append(tool.vla_complex)
        
        asyncio.run(self.joint_start(vlacs_to_start))

    async def joint_start(self, vlacs: List[VLA_Complex]):
        vla_complex_module.runner = self.get_runner()
        #print(f"Set vla_complex.runner: {vla_complex_module.runner.__name__}")

        for vlac in vlacs:
            await vlac.start()
        while True:
            await asyncio.sleep(60)
            
    async def start_vlac(self, vlac: VLA_Complex):
        # start the "scheduler"
        
        vla_complex_module.runner = self.get_runner()
        await vlac.start()

        # keep main loop alive
        while True:
            await asyncio.sleep(60)
    
    def get_runner(self) -> Callable:
        if type(self.context_engine) == OrderedContextLLMEngine:
            #print("Starting GDA")
            tm = ThinkingMachine(self.context_engine)
            rerun_function = tm.rerun
            #print("Creating task...")
            asyncio.create_task(tm.start())
            #print("Task created.")
        else:
            #print("Not starting GDA")
            rerun_function = self.context_engine.run_identity
            #print(f"Runner = {rerun_function}")
        return rerun_function

    def get_chat_vla_complex(self) -> VLA_Complex:
        for tool in self.tools:
            if type(tool.vla_complex) is Chat:
                return tool.vla_complex
        raise ValueError(f"[VLA*] Missing chat complex! {self.tools}")