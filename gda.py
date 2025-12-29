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
        self.context = {}

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

    async def check(self, rerun_input, signature, mode=None):
        # Break context signal into contextual prompt
        
        

        return await self.run(json.loads(rerun_input))
        
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
        self.vla_complexes = []
        self.context = {}

        self.system = {"Instructions": instructions, "Status":OK}

        self.name = name
        self.goal = goal

        self.overhead_prompt = self.goal
        self.memory_lim_before_recompute = 4
        self.last_status = None
        self._applicable = True
        self.running = False
        self.agent_identities = 0
        

    @property
    def applicable(self):
        return self._applicable
    
    @applicable.setter
    def applicable(self, value):
        self._applicable = value

    def set_tools(self, vlacs):
        for vlac in vlacs:
            self.vla_complexes.append(vlac)
            self.set_vla_complex(vlac)        

    def set_vla_complex(self, vlac):
        print(f"{vlac.tool_name} linked to {self.name}")
        self.tools.append(function_tool(
            vlac.execute,
            name_override=vlac.tool_name
        ))
        vlac.parent = self # The complex's check will go to this Agent
    
    async def spin_off_async(self, agent, prompt):
        try:
            log(f"Agent {agent.name} is started.", self)
            result = await Runner.run(agent, json.dumps(prompt))
            log(f"Agent {agent.name} is finished.", self)
        except Exception as e:
            print(f"!!Failed to run {agent.name}!!\nError:\n\t{e}")

    async def run(self, context=None):
        """ Context includes prompt. """
        self.applicable = True # output will be carried out
        
        agent = Agent(
            name=self.name + str(self.agent_identities),
            instructions=self.system_to_instructions(), # Yet to modify system instructions significantly
            tools=self.tools, # The tool-ified VLA Complexes
            model="o3-mini"
        )
        self.agent_identities += 1

        log(f"Context/prompt:\n{json.dumps(context)}", self)
        asyncio.create_task(self.spin_off_async(agent, context))
        while self.applicable:
            await asyncio.sleep(1) # should then wait until its done?

    async def check(self, rerun_input, signature="Anon"):
        """ A request to check an input from a VLA Complex ."""
        try: # Wrapped in a try
            log(f"Rerun input: {rerun_input} from {signature}.", self)
            self.context_from(rerun_input, signature) # Create context
            await self.run(self.context)
            return RERUN # return should be useful to VLA Complex
        except Exception as e:
            print(f"Error: {e}")

    def context_from(self, rerun_input: dict, signature: str):
        if not signature in self.context:
            self.context[signature] = {}
        for k, v in rerun_input.items():
            if not rerun_input[k] is None:
                if len(rerun_input[k]) > 0:
                    self.context[signature][k] = v

        for vlac in self.vla_complexes:
            if vlac.tool_name == signature:
                continue
            if not vlac.tool_name in self.context:
                # vlac.give_updates
                pass  

    def system_to_instructions(self):
        return json.dumps(self.system["Instructions"])

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