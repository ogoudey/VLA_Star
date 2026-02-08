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
from vla_complex import VLA_Complex
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
        self.tools = vlacs

    
import asyncio
import context_utils as cu
from context_utils import Context, OrderedContext
from vla_complex_state import State
"""
                                                -> DemoedLanguage
Stimulus -> Event -> AssembleContext -> Ordered -> RunAgentLock
internal      a           pull
   to       rerun        states
 VLA_C     request
"""





"""
   ...    rerun
    V       ^
raw state

"""

class PrototypeAgent:
    name: str
    agent_identities: int

    vla_complexes: List
    tools: List[FunctionTool]

    

    goal: Optional[str]
    def __init__(self, name):
        self.name = name
        self.agent_identities = 0

        self.vla_complexes = []
        self.tools = []

    def link_vla_complexes(self, vlacs):
        for vlac in vlacs:
            self.vla_complexes.append(vlac)
            self.set_as_tool(vlac)  
    
    def set_as_tool(self, vlac):
        print(f"{vlac.tool_name} linked to {self.name}")
        self.tools.append(function_tool(
            vlac.execute,
            name_override=vlac.tool_name
        ))
from summarizer_compressor import Summarizer

class ContextualAgent(PrototypeAgent):
    context: Context
    summarizer: Summarizer
    whether_to_always_summarize: bool

    def __init__(self, name, whether_to_always_summarize: bool = False):
        super().__init__(name)
        self.whether_to_always_summarize = whether_to_always_summarize
        self.summarizer = Summarizer()
        

    async def summarize_context(self):
        self.summarized_states = await self.summarizer.compress_all_states(self.vla_complexes)
        return self.summarized_states
    
    def update_context_with_summarization(self, summarized_states):
        self.summarizer.update_vla_complexes(self.vla_complexes, new_states)

    def context_init(self):
        if len(self.vla_complexes) == 0:
            raise ValueError("Not linked to any vla_complexes. Use `link_vla_complexes`.")
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
        while True:
            for tool in self.tools:
                print(f"{inspect.signature(tool.execute)}")
                task_name = input(f"{tool.tool_name}: ")
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

    def assemble_context(self, summarize:bool=True):
        self.context_init() # may be summarized or not
        self.order_context()
    


    async def request(self):
        if self.whether_to_always_summarize:
            await self.summarize_context()
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
            result = await Runner.run(self.identity, self.ordered_context, max_turns=3)
        except Exception as e:
            print(f"Wish I could cancel: {e}")
            return "This task is trash"
        
    def instance_system_prompt(self):
        system_prompt = self.instructions
        if self.goal:
            system_prompt += self.goal
        return system_prompt

          

    