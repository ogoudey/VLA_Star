from typing import List, Callable, Optional
import asyncio
import sys
from vla_star.context_engine import OrderedContextLLMEngine, OrderedContextEngineDemoed
from vla_complex.vla_complex import VLA_Complex
import vla_complex.vla_complex
from vla_star.runner import ThinkingMachine

from vla_star.agent_identifier import write_identifier


class VLA_Star:
    """
    Central class representing the agent
    """
    context_engine: OrderedContextLLMEngine | OrderedContextEngineDemoed
    vla_complexes: List[VLA_Complex]
    name: str

    def __init__(self, context_engine: OrderedContextLLMEngine | OrderedContextEngineDemoed, vla_complexes: List[VLA_Complex], name: str):
        self.context_engine = context_engine
        self.vla_complexes = vla_complexes
        self.context_engine.link_vla_complexes(vla_complexes)
        self.name = name

        write_identifier(self.name)
        vla_complex.agent_name = self.name # idk why i need this
        
    def safe_start(self):
        try:
            self.start()
        except KeyboardInterrupt as k:
            print("Exiting interaction.")

    def start(self, prompt: str | None = None):
        vlacs_to_start = []
        for vlac in self.vla_complexes:
            if hasattr(vlac, "start"):
                vlacs_to_start.append(vlac)
                print(f"Will start {vlac.tool_name}")
        
        asyncio.run(self.joint_start(vlacs_to_start))
        print(f"After for loop of all starting with a VLA Complex.")

    async def joint_start(self, vlacs: List[VLA_Complex]):
        for vlac in vlacs:
            print(f"Starting {vlac.tool_name}...")
            rerun_function = self.get_runner()
            await vlac.start(rerun_function)
        while True:
            await asyncio.sleep(60)
            
    async def start_vlac(self, vlac: VLA_Complex):
        # start the "scheduler"
        
        rerun_function = self.get_runner()
        await vlac.start(rerun_function)

        # keep main loop alive
        while True:
            await asyncio.sleep(60)
    
    def get_runner(self) -> Callable:
        if type(self.context_engine) == OrderedContextLLMEngine:
            print("Starting GDA")
            tm = ThinkingMachine(self.context_engine)
            rerun_function = tm.rerun
            print("Creating task...")
            asyncio.create_task(tm.start())
            print("Task created.")
        else:
            print("Not starting GDA")
            rerun_function = self.context_engine.run_identity
            print(f"Runner = {rerun_function}")
        return rerun_function