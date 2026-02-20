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
import os
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
            if hasattr(vlac, "execute"):
                self.set_as_tool(vlac)  
    
    def set_as_tool(self, vlac):
        print(f"{vlac.tool_name} linked to {self.name}")
        self.tools.append(function_tool(
            vlac.execute,
            name_override=vlac.tool_name
        ))


from pathlib import Path
from summarizer_compressor import Summarizer

class ContextualAgent(PrototypeAgent):
    context: Context
    summarizer: Summarizer
    whether_to_always_summarize: bool
    frozen_memory_dir: Path

    def __init__(self, name, whether_to_always_summarize: bool = False):
        super().__init__(name)
        self.whether_to_always_summarize = whether_to_always_summarize
        self.summarizer = Summarizer()
        self.frozen_memory_dir = Path("frozen") / self.name
        self.load_memory_dir_if_exists()
        
    def load_memory_dir_if_exists(self):
        
        if self.frozen_memory_dir.exists():
            core_memory_filename = self.frozen_memory_dir / "core.json"
            with open(core_memory_filename, "r") as file:
                f = file.read()
                x = json.loads(f)
            self.update_states_with_frozen_memory(x)
            print(f"Loaded core memory for {self.name}.")
        else:
            print(f"New agent created... {self.name}")

    def write(self):
        states = State.form_map_from_vlac_name_to_vlac_state(self.vla_complexes)
        states_json = State.states_to_json(states)
        if not self.frozen_memory_dir.exists():
            self.frozen_memory_dir.mkdir(parents=True, exist_ok=True)
        
        frozen_memory_filename = self.frozen_memory_dir / "core.json"
        with open(frozen_memory_filename, "w") as f:
            f.write(states_json)
        print(f"Saved core memory as {frozen_memory_filename}")
    
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

    def update_states_with_frozen_memory(self, states_json):
        print(states_json)
        print("\n\n")
        for vla_complex in self.vla_complexes:
            print(vla_complex)
            if vla_complex.state.session:
                vla_complex.state.session = states_json[vla_complex.tool_name]["session"]
            if vla_complex.state.impression:
                vla_complex.state.impression = states_json[vla_complex.tool_name]["impression"]

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

import threading
import socket
from chat_utils import recv_loop, send_loop
import queue

class OrderedContextDemoed(OrderedContextAgent):
    def __init__(self, name="Dev"):
        super().__init__(name)
        self.running_remote = False
        self.remote_port_if_needed = 5010
        self.send_q = queue.Queue()
        self.inbound_q = queue.Queue()

    def run_identity(self, source: str = "Anon"):
        try:
            self.context_init()
            self.order_context()
            self.write()
        except Exception as e:
            print(f"Failed to form and write context: {e}")
        if os.environ.get("DEMOED", None) == "REMOTE":
            if not self.running_remote:
                threading.Thread(target=self.run_server, daemon=True)
            self.remote_choice_loop()
        else:
            return self.local_choice_loop()

    def remote_choice_loop(self): 
        stripped_vla_complexes = self.strip_vla_complexes()
        self.send_q.put((self.ordered_context, stripped_vla_complexes))

    def run_server(self):
        print("Opening input socket...")
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", self.remote_port_if_needed))
            server.listen()
            self.running_remote = True
        except Exception as e:
            print(f"Failed to start chat server: {e}")
        print("Input server waiting...")
        while self.running_remote:
            client_sock, addr = server.accept()
            print("Input client connected:", addr)
            threading.Thread(
                target=self.handle_client,
                args=(client_sock,),
                daemon=True
            ).start()
                    
    def handle_client(self, sock):
        stop_event = threading.Event()

        threading.Thread(
            target=self.recv_loop,
            args=(sock, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=self.send_loop,
            args=(sock, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=self.respond_loop,
            args=(stop_event,),
            daemon=True
        ).start()
        try:
            while not stop_event.is_set():
                time.sleep(1)
        finally:
            stop_event.set()
            sock.close()

    def send_loop(self, sock: socket.socket, stop_event):
        try:
            while not stop_event.is_set():
                ordered_context, stripped_vla_complexes = self.send_q.get()
                sock.sendall((msg + "\n").encode()) # sends context
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            stop_event.set()

    def respond_loop(self, stop_event):
        try:
            while not stop_event.is_set():
                msg = self.inbound_q.get()
        except Exception as e:
            print(f"Error in respond loop!: {e}")

    def recv_line(self, sock: socket.socket):
        buffer = b""
        while not buffer.endswith(b"\n"):
            chunk = sock.recv(1)
            if not chunk:
                return None
            buffer += chunk
        return buffer.decode().strip()

    def recv_loop(self, sock: socket.socket, stop_event):
        try:
            while not stop_event.is_set():
                msg = self.recv_line(sock)
                if msg is None:
                    break
                self.inbound_q.put(msg)
        except (ConnectionResetError, OSError):
            pass
        finally:
            stop_event.set()

    def local_choice_loop(self):
        while True:
            print(f"{self.ordered_context}")
            for vla_complex in self.vla_complexes:
                print(f"____{vla_complex.tool_name}____")
                print(f"{inspect.signature(vla_complex.execute)}")
                choice = input(f"(\"\" to skip): ")
                if not choice == "":
                    args = []
                    for arg in list(inspect.signature(vla_complex.execute).parameters.keys()):
                        args.append(input(f"\t{arg}: ")) 
                    self.execute_vla_complex(vla_complex, *args)
                    return args
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
            context = str(self.ordered_context)
            print(f"___Prompt__\n{context}")
            self.write()
            result = await Runner.run(self.identity, context, max_turns=3)
        except Exception as e:
            print(f"Wish I could cancel: {e}")
            return "This task is trash"

    

    def instance_system_prompt(self):
        system_prompt = self.instructions
        if self.goal:
            system_prompt += self.goal
        return system_prompt