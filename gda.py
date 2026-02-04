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
import inspect
from exceptions import Shutdown

from displays import log, show_context, timestamp

from multiprocessing import Process


class DemoedLanguageModel:
    def __init__(self, goal: str = "Pass the proper args to your functions."):
        self.name = "Dev"
        self.applicable = True # actions always have effects
        self.goal = goal
        self.status_history = []
        self.context = {}

    def run_identity(self, rerun_input, source: str = "Anon"):
        print(f"Tools: {self.tools}")
        # assume one tool (the recorder)
        if len(self.tools) == 0:
            task_name = ""
            while task_name == "":
                
                task_name = input(f"\"{rerun_input}\" from {source}")
            self.use_tool(self.tools[0], task_name)
            return task_name
        else:
            while True:
                print(f"{source} ==> \"{rerun_input}\"")
                for tool in self.tools:
                    if hasattr(tool, "add_to_context"):
                        print(f"Tool's context: {json.dumps(tool.add_to_context(), indent=2)}")
                    print(f"{inspect.signature(tool.execute)}")
                    task_name = input(f"{tool.tool_name}: ")
                    print(f"{task_name}")
                    if not task_name == "":
                        task_name = task_name.split(",")
                        self.use_tool(tool, *task_name)
                        return task_name
                    else:
                        print(f"_______")
                print(f"Back to the top...")

    def use_tool(self, tool, *instruction):
        print("Using asyncio.run!")
        asyncio.run(tool.execute(*instruction))
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

    
import asyncio

pending_agents = []

class GDA:
    def __init__(self, name: str, instructions: str, goal:str | None = None):
        self.tools = []
        self.vla_complexes = []
        self.context = {}

        self.instructions = instructions
        self.goal = goal
        self.model = "o3-mini"
        self.name = name
        self.goal = goal

        self.memory_lim_before_recompute = 4
        self.last_status = None
        self._applicable = True
        self.running = False

        self.total_session_t0 = time.time()
        self.agent_identities = 0
        
        self.identities_running = 0

    def __str__(self):
        return f"LLM {self.name}"

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
    
    def instance_system_prompt(self):
        system_prompt = self.instructions
        if self.goal:
            system_prompt += self.goal
        return system_prompt

    async def run_identity(self, context):
        if self.identities_running > 0:
            print(f"(Identity running... waiting)")
            while self.identities_running < 0:
                time.sleep(0.1)

        identity = Agent(
            name=self.name + str(self.agent_identities),
            instructions=self.instance_system_prompt(),
            tools=self.tools, # The tool-ified VLA Complexes
            model=self.model,
        )
        self.agent_identities += 1

        context["Current time"] = timestamp()
        context["Session length"] = time.time() - self.total_session_t0
        prompt = json.dumps(context)
        show_context(context)

        self.clean_context()
        try:
            print(f"\t{identity.name} started.")
            self.identities_running += 1
            result = await Runner.run(identity, prompt, max_turns=2)
        except Exception as e:
            print(f"\tMax turns exceeded so just leaving it...")
            result = "Max turns exceeded."
        print(f"Hopefully {identity.name} is done.")
        self.identities_running -= 1
        return result

    def assemble_context(self, context: dict, from_source_signature: str):
        for vlac in self.vla_complexes:
            if not vlac.tool_name == from_source_signature:
                if hasattr(vlac, "add_to_context"):
                    context[vlac.tool_name] = vlac.add_to_context()
        return context


    def clean_context(self):
        #print(f"Cleaning {self.context}")
        if "Chat" in self.context:
            if "Current user message" in self.context["Chat"]:
                #print(f"Deleting {self.context["Chat"]["Current user message"]}")
                del self.context["Chat"]["Current user message"]

    def context_from(self, rerun_input: dict, signature: str):
        if not signature in self.context:
            self.context[signature] = {}
        for k, v in rerun_input.items():
            if not rerun_input[k] is None:
                if len(rerun_input[k]) > 0:
                    self.context[signature][k] = v

        for vlac in self.vla_complexes:
            
            
            if not vlac.tool_name in self.context:
                self.context[vlac.tool_name] = {}
                pass
            self.context[vlac.tool_name]["f"] = f"{round(vlac.use_frequency / (time.time() - self.total_session_t0), 3)} Hz"

        return self.context 

    def system_to_instructions(self):
        return json.dumps(self.instructions)

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