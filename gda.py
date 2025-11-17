from agents import Agent, Runner, function_tool
import asyncio
from signals import OK, CONTINUE, RERUN
import time
from threading import Thread
from typing import List
from itertools import groupby
import json


class GDA(Agent):

    def __init__(self, name: str, drivers, instructions: str):
        tools = []
        if drivers:
            for driver in drivers:
                tools.append(function_tool(driver.execute))

        self.system = {"Instructions": instructions, "Status":OK}
        super().__init__(
            name=name,
            instructions=system_to_instructions(self.system),
            tools=tools,
            model="o3-mini"
        )

        self.overhead_prompt = None
        self.memory_lim_before_recompute = 4
        self.last_status = None

        self.running = False

    

    def set_drivers(self, drivers):
        tools = []
        for driver in drivers:
            tools.append(function_tool(driver.execute))
        self.tools.extend(tools)


    def spin_off(self, prompt):
        thread_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(thread_loop)
        try:
            while True:

                if not self.running:
                    print(f"{self.instructions}")
                    print(f"Starting Agent with {prompt}")
                    result = Runner.run_sync(self, prompt)
                    print("Agent done.")
                    if result:
                        print(result.final_output)
                    self.running = True
                    break
        finally:
            thread_loop.stop()
        # stop when response acquired...

    async def run(self, prompt, extra=""):
        self.overhead_prompt = prompt
        thread = Thread(target=self.spin_off, args=[prompt + extra])
        thread.daemon = True 
        thread.start()
        time.sleep(20)
        #print(f"Joining {self.name}")
        thread.join()
            
    def adjust(self, status: str):
        self.system["Status"] = status
        self.instructions = system_to_instructions(self.system)

    async def check(self, status, recent_memory: List | None = None):
        self.last_status = status
        input = self.overhead_prompt
        # All checks should take into account recent memory / execution cache
        #print(f"Memory: {recent_memory}")
        if recent_memory:
            if len(recent_memory) > self.memory_lim_before_recompute:
                self.adjust(status)
                await self.run(input, extra=f"\n\nRecently you've performed {merge_past(recent_memory)}")
                return RERUN
        
        if status == OK:
            return CONTINUE
        else:
            self.adjust(status)
            await self.run(input)
            return RERUN


def system_to_instructions(system):
    return json.dumps(system)

def merge_past(lst):
    """
    Merge consecutive identical instructions in a list of the form:
    [instr1, dur1, instr2, dur2, ...]
    Returns a list of tuples: [(instr, total_duration), ...]
    """
    merged = ""
    # pair instructions with durations
    it = iter(lst)
    pairs = list(zip(it, it))  # [('stop', 2.72), ('stop', 2.86), ...]
    
    for instr, group in groupby(pairs, key=lambda x: x[0]):
        total_duration = sum(dur for _, dur in group)
        merged += f"\"{instr}\" for {total_duration} seconds, then "

    return merged + "..."