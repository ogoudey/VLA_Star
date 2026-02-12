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
    
    def whether_to_summarize(self) -> bool:
        if self.whether_to_always_summarize:
            val = True
        else:
            if self.total_complex_event_cnt() > 10:
                val = True
            else:
                val = False
        verbose = "Summarizing..." if val else "Not summarizing."
        print(verbose)
        return val
    
    def total_complex_event_cnt(self):
        cnt = 0
        for vlac in self.vla_complexes:
            if vlac.state.session:
                cnt += len(vlac.state.session)
        return cnt


    async def summarize_states(self):
        self.summarized_states = await self.summarizer.compress_all_states(self.vla_complexes)
        return self.summarized_states
    
    def update_states_with_summarization(self, summarized_states):
        self.summarizer.update_vla_complexes(self.vla_complexes, summarized_states)

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


class OrderedContextDemoed(OrderedContextAgent):
    def __init__(self):
        super().__init__("Dev")

    def run_identity(self, source: str = "Anon"):
        while True:
            self.context_init()
            self.order_context()
            print(f"{self.ordered_context}")
            for vla_complex in self.vla_complexes:
                print(f"____{vla_complex.tool_name}____")
                print(f"{inspect.signature(vla_complex.execute)}")
                task_name = input(f"(\"\" to skip) args: ")
                if not task_name == "":
                    task_name = task_name.split(",")
                    self.execute_vla_complex(vla_complex, *task_name)
                    return task_name
                else:
                    print(f"_______")
            print(f"\nV V V V V\n")

    def execute_vla_complex(self, vla_complex, *instruction):
        asyncio.run(vla_complex.execute(*instruction))

from one_identity_at_a_time import SingleIdentityRunningLock


class OrderedContextLLMAgent(OrderedContextAgent):
    instructions: str
    goal: Optional[str]
    model: str
    identity: Agent
    identity_lock: SingleIdentityRunningLock

    def __init__(self, name: str, instruction: str, goal: Optional[str] = None):
        super().__init__(name)
        self.instructions = instruction
        self.goal = goal

        self.model="o4-mini"
        self.identity_lock = SingleIdentityRunningLock()

    def assemble_context(self):
        self.context_init() # may be summarized or not
        self.order_context()

    async def request(self):
        print(f"Agent requested...")
        if self.whether_to_summarize():
            ss = await self.summarize_states()
            self.update_states_with_summarization(ss)
        try:
            async with self.identity_lock:
                self.assemble_context()
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
            model=self.model
        )

    async def run_the_identity(self):
        try:
            prompt = str(self.ordered_context)
            print(f"___Prompt__\n{prompt}")
            result = await Runner.run(self.identity, prompt, max_turns=3)
        except Exception as e:
            print(f"Wish I could cancel: {e}")
            return "This task is trash"
        
    def instance_system_prompt(self):
        system_prompt = self.instructions
        if self.goal:
            system_prompt += self.goal
        return system_prompt

          

    