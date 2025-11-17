
from gda import GDA
from vlm import VLM
import time

from signals import DONE
from signals import CONTINUE, RERUN

import asyncio


class VLA:
    """Takes a function that takes a string. Can be called like VLA()(...)"""
    def __init__(self):
        pass

    def __call__(self, direction: str):
        raise NotImplementedError



class VLA_Complex:
    def __init__(self, parent: GDA, monitor: VLM, vla: VLA, capability_desc: str):
        self.parent = parent
        self.monitor = monitor
        self.vla = vla
        self.execute.__func__.__doc__ = capability_desc

        self.monitor_sleep_period = 2.0
        self.execution_cache_max = 12
        self.execution_cache = []
        self.last_instruction = None

    async def execute(self, instruction: str):
        """____"""
        vlm_prompt = f"Are we good to {instruction} given that we just did {self.last_instruction}? (OK | ...)" if self.last_instruction else f"Are we good to {instruction}? (OK | ...)"
        #print(f"Executing {instruction}")
        status = self.monitor.status(vlm_prompt) # Starter
        check = await self.parent.check(status)
        if check == RERUN:
            return "Done."
        
        while check == CONTINUE:
            self.vla(instruction)
            t = time.time()
            time.sleep(self.monitor_sleep_period)
            self.last_instruction = instruction
            self.execution_cache.extend([instruction, time.time() - t])
            status = self.monitor.status(f"Can we continue to {instruction}? (OK | ... | DONE)") # Continuer
            if status == DONE:
                return "Done"
            check = await self.parent.check(status, self.execution_cache)
            if check == RERUN:
                return "Done."
            
            #print(self.execution_cache)
            
            if len(self.execution_cache) > self.execution_cache_max:
                self.execution_cache.pop(0)
                self.execution_cache.pop(0)
                #print(f"Forgetting... -> ", self.execution_cache)

class VLA_Star:
    name: str
    vlm: VLM
    agent: GDA
    vla: VLA_Complex

    def __init__(self, name: str, vlm: VLM | None = None, agent: GDA | None = None):
        self.vlm = vlm
        self.agent = agent

    @property
    def initialized(self):
        if self.vlm is None:
            return False
        if self.agent is None:
            return False
        # etc
        return True
    
    async def run(self, prompt):
        if not self.initialized:
            raise Exception("VLA* not fully initialized.")
        
        await self.agent.run(prompt)




from transmitters import ThroughMessage


class SimpleDrive(VLA):
    def __init__(self):
        super().__init__()
        self.shared = {"target_message": "stop"}
        through_thread = ThroughMessage(self.shared)
        through_thread.start()
        
    def __call__(self, direction: str):
        #print(f"Setting target message to {direction}")
        self.shared["target_message"] = direction

def main():

    driving_monitor = VLM("driving_monitor", "You are the perception system for a car, noting the status of a mission. Given the query, return either OK or a descriptive response.")

    agent = GDA("decision-maker", None, \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Your ultimate goal is to safely drive down the street. To do so you must call your function. However, you can only reach your goal one step at a time. Return one and ONLY one \"step\" of your journey. Your final output doesn't matter, only the one function call. Simple!" \
    "")

                    
    vla = SimpleDrive()

    driver = VLA_Complex(agent, driving_monitor, vla, \
    "Use a model to perform the instruction. Only make one tool call. This model's capabilities are to go forward, turn an angle, or halt:" \
    "" \
    "instruction: \"forward\" | \"turn mn\" | \"turn -n\" | \"stop\" (where n is an angle in degrees)")

    agent.set_drivers([driver])

    drive = VLA_Star("drive_down_the_street", driving_monitor, agent)

    asyncio.run(drive.run("Drive safely, obeying the rules of the road (MA law)."))

if __name__ == "__main__":
    main()