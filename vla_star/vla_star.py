from typing import List, Callable
import asyncio
import sys
from gda import OrderedContextLLMAgent, OrderedContextDemoed, PrototypeAgent
from vla_complex.vla_complex import VLA_Complex
import vla_complex.vla_complex
from runner import ThinkingMachine

class VLA_Star:
    """
    Central class representing the agent
    """
    agent: OrderedContextLLMAgent | OrderedContextDemoed
    vla_complexes: List[VLA_Complex]

    def __init__(self, prototype_agent: OrderedContextLLMAgent | OrderedContextDemoed, vla_complexes: List[VLA_Complex]):
        self.prototype_agent = prototype_agent
        self.vla_complexes = vla_complexes
        self.prototype_agent.link_vla_complexes(vla_complexes)

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
        vla_complex.agent_name = self.prototype_agent.name
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
        if type(self.prototype_agent) == OrderedContextLLMAgent:
            print("Starting GDA")
            tm = ThinkingMachine(self.prototype_agent)
            rerun_function = tm.rerun
            print("Creating task...")
            asyncio.create_task(tm.start())
            print("Task created.")
        else:
            print("Not starting GDA")
            rerun_function = self.prototype_agent.run_identity
            print(f"Runner = {rerun_function}")
        return rerun_function