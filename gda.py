import sys
from agents import Agent, Runner, function_tool
import asyncio
from signals import OK, CONTINUE, RERUN
import time
from threading import Thread
from typing import List
from itertools import groupby
import json
import random

from logger import log

from multiprocessing import Process


class DemoedLanguageModel:
    def __init__(self, goal: str = "Pass the proper args to your functions."):
        self.applicable = True # actions always have effects
        self.goal = goal

        self.status_history = []

    async def run(self, prompt="You got this..."):
        
        # assume one tool (the recorder)
        if len(self.tools) == 0:
            task_name = ""
            while task_name == "":
                task_name = input(f"Goal: {self.goal}\nPrompt: {prompt}\nTask label: ")
            await self.tools[0].execute(task_name)
            return task_name
        else:
            while True:
                for tool in self.tools:
                    task_name = input(f"\n___Modality name: {tool.tool_name}___\nGoal: {self.goal}\nDocstring: {tool.execute.__func__.__doc__}\nPrompt: {prompt}\nInput ([enter] to bypass): ")
                    if not task_name == "":
                        await tool.execute(task_name)
                        return task_name
                print(f"Back to the top...")

        """
        for vlac in self.tools:
            inp = input(f"({vlac.tool_name}) {vlac.capability_desc}: ")
            if not inp == "":
                tool_instructions[vlac]
        for tool, instruction in tool_instructions.items():
            tool(instruction)
        """

    async def check(self, rerun_input, mode=None):
        # Break context signal into contextual prompt

        # or not...
        return await self.run(rerun_input)
        
        if mode == "EXIT_E":
            task_name = input("New task name? (^C to exit, [enter] to use same task name): ")
            return "CONTINUE", task_name
        
        if mode == "EXIT_LOOP":
            dataset_name = input("Dataset name ([enter] to delete dataset): ")
            return "CONTINUE", dataset_name
        return "RERUN"

    def set_tools(self, vlacs):
        for vlac in vlacs:
            vlac.parent = self
        self.tools = vlacs



class GDA:
    

    def __init__(self, name: str, instructions: str, goal:str | None = None):
        self.tools = []
        self.system = {"Instructions": instructions, "Status":OK}
        self.name = name
        self.goal = goal
        self.overhead_prompt = self.goal
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

    def set_tools(self, vlacs):
        self.set_vla_complexes(vlacs)

    def set_vla_complexes(self, vlacs):
        for vlac in vlacs:
            self.set_vla_complex(vlac)

    def set_vla_complex(self, vlac):
        method = vlac.execute
        self.tools.append(function_tool(
            method,
            #name_override=method.__self__.__class__.tool_name
            name_override=vlac.tool_name
        ))
        vlac.parent = self
    

    def spin_off(self, agent, prompt):
        
        Runner.run_sync(agent, prompt)
        self.running_agents -= 1

    async def spin_off_async(self, agent, prompt):
        log(f"Running new decision-maker...", self)
        try:
            result = await Runner.run(agent, json.dumps(prompt))
        except Exception as e:
            print(f"!!OOps! {e}!!")

    async def run(self, prompt=None):
        self.applicable = True
        if not self.overhead_prompt:
            if not prompt:
                raise Exception("No goal for GDA given.")
            self.overhead_prompt = prompt
        self.running_agents += 1
        
        agent = Agent(
            name=self.name + str(self.running_agents),
            instructions=system_to_instructions(self.system),
            tools=self.tools,
            model="o3-mini"
        )
        log(f"Spinning off agent.", self)
        asyncio.create_task(self.spin_off_async(agent, prompt))
        while self.applicable:
            await asyncio.sleep(1) # should then wait until its done?
        #thread = Thread(target=self.spin_off, args=[agent, prompt], daemon=True)
        #thread.start()
            


    async def check(self, rerun_input, recommendation=None, recent_memory: List | None = None):
        input = rerun_input
        if recommendation:
            input += f"\nRecommendation (from a vision system): {recommendation}"
        # All checks should take into account recent memory / execution cache
        #print(f"Memory: {recent_memory}")
        if recent_memory:
            if len(recent_memory) > 0:
                input += f"\n\nRecently you've performed {merge_past(recent_memory)}"
                if len(recent_memory) > self.memory_lim_before_recompute:
                    print(f"Recomputing due to memory.   ↵")
                    
                    if recommendation:
                        print(f"Recommendation from VLA complex {recommendation}")
                    await self.run(input)
                    return RERUN
        
        if rerun_input == OK:
            return CONTINUE
        else:
            log(f"Recomputing due to {rerun_input} status from child.", self)
            if recommendation:
                print(f"Recommendation from VLA complex {recommendation}")
            log(f"Running agent... {input}", self)
            await self.run(input)
            return RERUN


def system_to_instructions(system):
    return json.dumps(system["Instructions"])

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