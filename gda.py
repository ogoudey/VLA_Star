import sys
from agents import Agent, Runner, function_tool, RunConfig, FunctionTool
import asyncio
from signals import OK, CONTINUE, RERUN
import time
from threading import Thread
from typing import List, Any, Optional
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

    def run_identity(self, source: str = "Anon"):
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


    def set_tools(self, vlacs):
        for vlac in vlacs:
            vlac.parent = self
        self.tools = vlacs

    
import asyncio
import context_utils as cu
from context_utils import Context, OrderedContext

"""
                                                -> DemoedLanguage
Stimulus -> Event -> AssembleContext -> Ordered -> RunAgentLock
internal      a           pull
   to       rerun        states
 VLA_C     request
"""

class PrototypeAgent:
    name: str
    tools: List[FunctionTool]
    vla_complexes: List
    agent_identities: int

    goal: Optional[str]
    def __init__(self, name):
        self.name = name

    

class ContextualAgent(PrototypeAgent):
    context: Context
    def __init__(self, name):
        super().__init__(name)
    def context_init(self):
        self.context = Context(self.vla_complexes) # make context from vla_complexes

class OrderedContextAgent(ContextualAgent):
    ordered_context: OrderedContext
    def __init__(self, name):
        super().__init__(name)
    def order_context(self):
        self.ordered_context = OrderedContext(self.context)

from one_identity_at_a_time import SingleIdentityRunningLock

class OrderedContextDemoed(OrderedContextAgent):
    def __init__(self, name):
        super().__init__(name)


    def run_identity(self):
        """
        From where is this called? Time to look back at VLA_Complexes
        """
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

class OrderedContextLLMAgent(OrderedContextAgent):
    instructions: str
    model: str
    identity: Agent
    identity_lock: SingleIdentityRunningLock

    def __init__(self, name: str, instruction: str, goal: str):
        super().__init__(name)
        self.identity_lock = SingleIdentityRunningLock()

    def assemble_context(self):
        self.context_init()
        self.order_context()

    async def request(self):
        self.assemble_context()
        try:
            with self.identity_lock:
                await self.run_identity()
        except RuntimeError:
            print("Identity rejected...")
    
    async def run_identity(self):
        self.create_identity()
        await self.run_the_identity()
        
    def create_identity(self):
        self.identity = Agent(
            name=self.name + str(self.agent_identities),
            instructions=self.instance_system_prompt(),
            tools=self.tools, # The tool-ified VLA Complexes
            model=self.model,
            run_config=RunConfig(
                seed=42,
                temperature=0
            )
        )

    async def run_the_identity(self):
        try:
            result = await Runner.run(self.identity, self.ordered_context, max_turns=2)
        except Exception as e:
            print(f"Wish I could cancel: {e}")
            return "This task is trash"
        
    def instance_system_prompt(self):
        system_prompt = self.instructions
        if self.goal:
            system_prompt += self.goal
        return system_prompt
        

class GDA(PrototypeAgent):
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
        self.waiting_to_run = False
        self.has_new_thought = False

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
        if self.waiting_to_run:
            self.has_new_thought = True
            time.sleep(0.11)
        if self.identities_running > 0:
            self.waiting_to_run = True
            
            while self.identities_running > 0 and not self.has_new_thought:
                time.sleep(0.1)
                
        self.waiting_to_run = False
        identity = Agent(
            name=self.name + str(self.agent_identities),
            instructions=self.instance_system_prompt(),
            tools=self.tools, # The tool-ified VLA Complexes
            model=self.model,
            run_config=RunConfig(
                seed=42,
                temperature=0
            )
        )
        self.agent_identities += 1

        context["Current time"] = timestamp()
        context["Session length"] = time.time() - self.total_session_t0
        prompt = json.dumps(context)
        show_context(context)

        self.clean_context()
        try:
            
            self.identities_running += 1
            print(f"\t{identity.name} started. identities_running = {self.identities_running}")
            result = await Runner.run(identity, prompt, max_turns=2)
            print(f"Hopefully {identity.name} is done.")
            self.identities_running -= 1
            return result
        except Exception as e:
            print(f"Wish I could cancel: {e}")
            return "This task is trash"

    

    def context_from(self, rerun_input: dict, signature: str):
        if type(rerun_input) == str:
            rerun_input = {"Notification": rerun_input}
        if not signature in self.context:
            self.context[signature] = {}
        for k, v in rerun_input.items():
            if rerun_input[k]:
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