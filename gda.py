import sys
print(sys.path)

from agents import Agent, Runner, function_tool
import asyncio
from signals import OK, CONTINUE, RERUN
import time
from threading import Thread
from typing import List
from itertools import groupby
import json
import random

from multiprocessing import Process


class GDA:

    def __init__(self, name: str, drivers, instructions: str):
        self.tools = []
        if drivers:
            self.set_drivers(drivers)
        self.system = {"Instructions": instructions, "Status":OK}
        self.name = name

        self.overhead_prompt = None
        self.memory_lim_before_recompute = 4
        self.last_status = None
        self._applicable = True
        self.running = False
        self.running_agents = 0

    @property
    def applicable(self):
        return self._applicable
    
    @applicable.setter
    def applicable(self, value):
        self._applicable = value

    def set_drivers(self, drivers):
        tools = []
        for driver in drivers:
                method = driver.execute
                print(type(driver))
                print(method.__self__.__class__)
                tools.append(function_tool(
                    method,
                    #name_override=method.__self__.__class__.tool_name
                    name_override=driver.tool_name
                ))
        self.tools.extend(tools)

    

    def spin_off(self, agent, prompt):
        
        Runner.run_sync(agent, prompt)
        self.running_agents -= 1

    async def spin_off_async(self, agent, prompt):
        print(f"Running new decision-maker...")
        result = await Runner.run(agent, prompt)

    async def run(self, prompt):
        self.applicable = True
        if not self.overhead_prompt:
            self.overhead_prompt = prompt
        self.running_agents += 1
        
        agent = Agent(
            name=self.name + str(self.running_agents),
            instructions=system_to_instructions(self.system),
            tools=self.tools,
            model="o3-mini"
        )
        
        


        asyncio.create_task(self.spin_off_async(agent, prompt))
        await asyncio.sleep(10)
        #thread = Thread(target=self.spin_off, args=[agent, prompt], daemon=True)
        #thread.start()

        

            
    def adjust(self, status: str):
        self.system["Status"] = status
        self.instructions = system_to_instructions(self.system)

    async def check(self, status, recommendation=None, recent_memory: List | None = None):
        self.last_status = status
        
        input = f"{self.overhead_prompt}\nStatus: {self.system['Status']}"
        if recommendation:
            input += f"\nRecommendation (from a vision system): {recommendation}"
        # All checks should take into account recent memory / execution cache
        #print(f"Memory: {recent_memory}")
        if recent_memory:
            if len(recent_memory) > 0:
                input += f"\n\nRecently you've performed {merge_past(recent_memory)}"
                if len(recent_memory) > self.memory_lim_before_recompute:
                    print(f"Recomputing due to memory.   ↵")
                    
                    self.adjust(status)
                    if recommendation:
                        print(f"Recommendation from VLA complex {recommendation}")
                    await self.run(input)
                    return RERUN
        
        if status == OK:
            return CONTINUE
        else:
            print(f"Recomputing due to {status} status from child.")
            self.adjust(status)
            if recommendation:
                print(f"Recommendation from VLA complex {recommendation}")
            await self.run(input)
            return RERUN


def system_to_instructions(system):
    return system["Instructions"]
    return json.dumps(system)

def merge_past(lst):
    """
    Merge consecutive identical instructions in a list of the form:
    [instr1, dur1, instr2, dur2, ...]
    
    Returns a string like:
    '"stop" for 5.58 seconds, then "move" for 3.2 seconds, then mostly recently you have done "move"'
    """
    if not lst:
        return "No instructions"

    # Pair instructions with durations
    it = iter(lst)
    pairs = list(zip(it, it))  # [('stop', 2.72), ('stop', 2.86), ...]

    merged_parts = []

    # Group consecutive identical instructions
    for instr, group in groupby(pairs, key=lambda x: x[0]):
        total_duration = sum(dur for _, dur in group)
        merged_parts.append(f'"{instr}" for {total_duration:.2f} seconds')

    # Construct the final string
    if merged_parts:
        *all_but_last, last = merged_parts
        if all_but_last:
            return ", then ".join(all_but_last) + f", then mostly recently you have done {last.split(' ')[0]}"
        else:
            return f"Mostly recently you have done {last.split(' ')[0]}"
    else:
        return "No instructions"