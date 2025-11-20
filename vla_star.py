
from gda import GDA
from vlm import VLM
import time
from typing import List
from signals import DONE
from signals import CONTINUE, RERUN

import asyncio

RAW_EXECUTE = True

class VLA:
    """Takes a function that takes a string. Can be called like VLA()(...)"""
    def __init__(self):
        pass

    def __call__(self, direction: str):
        raise NotImplementedError



class VLA_Complex:
    tool_name: str
    def __init__(self, tool_name: str, parent: GDA, monitor: VLM, vla: VLA, capability_desc: str):
        self.parent = parent
        self.monitor = monitor
        self.vla = vla
        self.execute.__func__.__doc__ = capability_desc

        self.monitor_sleep_period = 2.0
        self.execution_cache_max = 12
        self.execution_cache = []
        self.last_instruction = None
        
        self.tool_name = tool_name

    async def execute(self, instruction: str):
        """____"""
        if not self.parent.applicable:
            return f"Inapplicable call. Please finish execution (no final response needed)."
        print(f"\t\"{instruction}\" presented to VLA Complex")

        if RAW_EXECUTE:
            self.vla(instruction)
            return f"Done. Call no more tools and return."


        self.parent.applicable = False
        monitor_prompt = f"Are we good to {instruction} given that we just did {self.last_instruction}? (OK | ...)" if self.last_instruction else f"Are we good to {instruction}? (OK | ...)"

        recommendor_prompt = f"What action shall we take in order to {self.parent.overhead_prompt}"


        status = self.monitor.status_sync(monitor_prompt) # Continuer

        


        # Just a monitor's status
        #status = self.monitor.status(vlm_prompt) # Starter
        
        
        
        
        check = await self.parent.check(status)
        if check == RERUN:
            return f"Done. Call no more tools and return."
        self.execution_cache = []
        while check == CONTINUE:
            self.vla(instruction)
            print(f"\t\tContinuing to do \"{instruction}\"")
            t = time.time()
            await asyncio.sleep(self.monitor_sleep_period)
            self.last_instruction = instruction
            self.execution_cache.extend([instruction, time.time() - t])

            monitor_prompt = f"Can we continue to \"{instruction}\"? (OK | ... | DONE)"

            taskA = asyncio.create_task(self.monitor.status(monitor_prompt))
            taskB = asyncio.create_task(self.monitor.recommendation(recommendor_prompt))

            # Wait for both to finish and get results
            status, recommendation = await asyncio.gather(taskA, taskB)


            if status == DONE:
                print(f"\t\tDone with \"{instruction}\"")
                return "Done"
            
            if status == RERUN:
                print(f"\t\tWon't continue \"{instruction}\" because \"{status}\"")

            check = await self.parent.check(status, recommendation, self.execution_cache) # Don't print after this
            if len(self.execution_cache) > self.execution_cache_max:
                self.execution_cache = []
            if check == RERUN:
                return "Done."
            
            #print(self.execution_cache)
            
            
                #self.execution_cache.pop(0)
                #self.execution_cache.pop(0)
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
        while True:
            await asyncio.sleep(1)




from transmitters import ThroughMessage


class SimpleDrive(VLA):
    def __init__(self):
        super().__init__()
        self.shared = {"target_message": "stop"}
        through_thread = ThroughMessage(self.shared)
        through_thread.start()
        
        
    def __call__(self, direction: str):
        self.shared["target_message"] = direction

from pathlib import Path
import sys
sys.path.append("/home/olin/Robotics/AI Planning/Path-Planning")
import space

class PathFollow(VLA):
    def __init__(self):
        super().__init__()
        self.plans = dict[str, List]
        print(space.__file__)

    def __call__(self, goal: str):
        print(f"Pathing to {goal}")
        try:
            self.plan(goal)
        except Exception as e:
            raise Exception(e)

    def plan(self, goal):
        import terrain_fetcher
        print("imported")
        heightmap = terrain_fetcher.get_terrain()
        print(heightmap)

        # Turn it into space
        # A*
        # Set path and follow

    def follow(self):
        self.shared = {"target_message": "stop"}
        through_thread = ThroughMessage(self.shared)
        through_thread.start()

### Demos ###
def street_and_crosswalks():
    driving_monitor = VLM("driving_monitor", "You are the perception system for a car, noting the status of a mission. Given the query, return either OK or a descriptive response.")

    agent = GDA("decision-maker", None, \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Your ultimate goal is to safely drive down the street. To do so you must call your function. However, you can only reach your goal one step at a time. Return one and ONLY one \"step\" of your journey. Your final output doesn't matter, only the one function call. Simple!" \
    "")

                    
    vla = SimpleDrive()

    driver = VLA_Complex("drive", agent, driving_monitor, vla, \
    "Use a model to perform the instruction. Only make one tool call. This model's capabilities are to go forward, turn an angle, or halt:" \
    "" \
    "instruction: \"forward\" | \"turn +n\" (degrees to the right)| \"turn -n\" (degrees to the left)| \"stop\"" \
    "A turn will only apply once. It will not repeat unless you provide a new angle.")

    agent.set_drivers([driver])

    drive = VLA_Star("drive_down_the_street", driving_monitor, agent)

    asyncio.run(drive.run("Drive safely, obeying the rules of the road (MA law)."))

def navigate_river():
    driving_monitor = VLM("driving_monitor", system_prompt="You are the perception system for a boat, and take note of the status of the mission. Given the query, return either OK or a descriptive response. (The boat can only go forward, turn in units degrees, or stop, and is very unmaneuverable.)",
                          recommendation_system_prompt="You are a navigation system for a boat, suggesting \"forward\", \"turn left n\", \"turn right n\", or \"stop\".")

    agent = GDA("decision-maker", None, \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Your ultimate goal is to navigate through the narrow brook safely (without hitting any land).\n" \
    "You may choose ANY of the available tools.\n"\
    "You must call exactly ONE tool.\n"\
    "After calling one tool, stop all further reasoning.\n"\
    "Do not produce natural-language output. "\
    "Return immediately after the tool call.\n")

                    
    vla = SimpleDrive()

    driver = VLA_Complex("drive", agent, driving_monitor, vla, \
    "Use a model to perform the instruction. Only make one tool call. This model's capabilities are to go forward, turn slightly (will keep moving), or halt:" \
    "" \
    "instruction: \"forward\" | \"turn left n\"| \"turn right n\"| \"stop\"")

    agent.set_drivers([driver])

    drive = VLA_Star("navigate_through_the_river", driving_monitor, agent)

    asyncio.run(drive.run("Navigate safely through the narrow brook."))

def follow_path_river():
    driving_monitor = VLM("driving_monitor", system_prompt="You are the perception system for a boat. Take note of the status of the mission. Given the query, return either OK or a descriptive response.")

    agent = GDA("decision-maker", None, \
    "You are a decision-making agent in a network of LLMs that compose a physical agent. Your ultimate goal is to navigate through the narrow brook safely (without hitting any land).\n" \
    "You may choose ANY of the available tools.\n"\
    "You must call exactly ONE tool.\n"\
    "After calling one tool, stop all further reasoning.\n"\
    "Do not produce natural-language output. "\
    "Return immediately after the tool call.\n")

                    
    vla = PathFollow()

    driver = VLA_Complex("drive", agent, driving_monitor, vla, \
    "Use a model to perform the instruction. Only make one tool call. This model's capabilities are to go to a locations from the following list:" \
    "dockA, dockB, center_of_pond")
    
    agent.set_drivers([driver])

    drive = VLA_Star("navigate_in_water", driving_monitor, agent)

    asyncio.run(drive.run("Get to dock B."))

def main():
    #navigate_river()
    follow_path_river()
    

if __name__ == "__main__":
    main()