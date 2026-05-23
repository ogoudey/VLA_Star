from typing import List, Callable, Optional
import asyncio
import sys
from vla_star.context_engine import OrderedContextLLMEngine, OrderedContextEngineDemoed
from vla_complex.vla_complex import VLA_Complex
import vla_complex.vla_complex as vla_complex_module
from vla_star.runner import ThinkingMachine



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
        vla_complex_module.agent_name = self.name # idk why i need this
        
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
                #print(f"Will start {vlac.tool_name}")
        
        asyncio.run(self.joint_start(vlacs_to_start))
        #print(f"After for loop of all starting with a VLA Complex.")

    async def joint_start(self, vlacs: List[VLA_Complex]):
        vla_complex_module.runner = self.get_runner()
        print(f"Set vla_complex.runner: {vla_complex_module.runner.__name__}")

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