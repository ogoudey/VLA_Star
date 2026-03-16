import sys
from agents import Agent, Runner, function_tool, FunctionTool
import asyncio
from signals import OK, CONTINUE, RERUN
import time
from threading import Thread
from typing import List, Any, Optional
from itertools import groupby
import json
import random
import inspect
import os
from displays import log, show_context, timestamp
from vla_complex import VLA_Complex
from multiprocessing import Process
from demoed_input import ChoiceData, VLA_ComplexStripped
import metrics
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

    def vla_complex_by_name(self, tool_name):
        for vlac in self.vla_complexes:
            if vlac.tool_name == tool_name:
                return vlac
        raise KeyError(f"Could not find VLA Complex by name {tool_name}")

from pathlib import Path
from summarizer_compressor import Summarizer
from agent_identifier import write_identifier

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
        
        
    def link_vla_complexes(self, vlacs):
        super().link_vla_complexes(vlacs)
        self.load_memory_dir_if_exists()
        
    def load_memory_dir_if_exists(self):
        core_memory_filename = self.frozen_memory_dir / "core.json"
        if core_memory_filename.exists():
            with open(core_memory_filename, "r") as file:
                f = file.read()
                x = json.loads(f)
            self.update_states_with_frozen_memory(x)
            print(f"Loaded core memory for {self.name}.")
        else:
            write_identifier(self.name)
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
        print("\n")
        for vla_complex in self.vla_complexes:
            if not vla_complex.tool_name in states_json:
                print(f"{vla_complex} not in memory. New VLA Complex?")
                continue
            else:
                print(f"{vla_complex} <== {states_json[vla_complex.tool_name]}")
            if vla_complex.state.session is not None:
                print(f"\t{vla_complex} session: {vla_complex.state.session} <== {states_json[vla_complex.tool_name]['session']}")
                vla_complex.state.session = states_json[vla_complex.tool_name]["session"]
                # Special case:
                if vla_complex.tool_name == "drive":
                    vla_complex.state.add_to_session("Meta-status", "Reinitialized position!")
            if vla_complex.state.impression is not None:
                print(f"\t{vla_complex} impression: {vla_complex.state.impression} <== {states_json[vla_complex.tool_name]['impression']}")
                vla_complex.state.impression = states_json[vla_complex.tool_name]["impression"]
                if vla_complex.tool_name == "drive":
                    vla_complex.state.impression.update({
                        "currently travelling": False,
                        "current position": "Initial position"
                    })

    def context_init(self):
        if len(self.vla_complexes) == 0:
            raise ValueError("Not linked to any vla_complexes. Use `link_vla_complexes`.")
        self.context = Context(self.vla_complexes) # make context from vla_complexes

from general_dataset import Dataset, ToolChoiceMade

class OrderedContextAgent(ContextualAgent):
    system: Optional[str]
    ordered_context: OrderedContext
    t0_identity_run: float
    recording: bool = False
    dataset: Optional[Dataset] = None
    

    def __init__(self, name):
        super().__init__(name)

    def order_context(self):
        self.ordered_context = OrderedContext(self.context)

    def write(self):
        super().write()
        if self.recording:
            if self.dataset is None:
                self.dataset = Dataset(self.name)
            self.dataset.add_to_frame(self.system)
            self.dataset.add_to_frame(self.ordered_context)
            self.dataset.add_to_frame(self.tools)
            self.dataset.timestamp_frame()

    def write_output(self, result: Any, metadata: dict):
        """
        result is LLM result (Runner.run()) or demoed_result
        """
        if self.recording:
            self.dataset.add_to_frame(result)
            self.dataset.add_metadata_to_frame(metadata)
            self.dataset.end_frame()

    def instance_system_prompt(self):
        raise NotImplementedError(f"Cannot record on {type(self)}")

import threading
import socket
from chat_utils import recv_loop, send_loop
import queue
from dataclasses import dataclass, asdict

class OrderedContextDemoed(OrderedContextAgent):
    running_remote: bool = False
    pseudo_system: Optional[str] = None
    
    def __init__(self, name):
        super().__init__(name)
        if os.environ.get("DEMOED", None) == "REMOTE":
            self.remote_port_if_needed = 5010
            self.send_q = queue.Queue()
            self.inbound_q = queue.Queue()

    def instance_system_prompt(self):
        self.system = self.pseudo_system
        
    def run_identity(self, source: str = "Anon"):
        if source == "STOP":
            print("STOPPING")
        try:
            self.instance_system_prompt()
            self.context_init()
            self.order_context()
            self.write()
        except Exception as e:
            print(f"Failed to form and write context: {e}")
        if os.environ.get("DEMOED", None) == "REMOTE":
            if not self.running_remote:
                threading.Thread(target=self.run_server, daemon=True).start()
            print("Sending remote choice!")
            self.remote_choice_loop()
        else:
            return self.local_choice_loop()

    def run_server(self):
        print("Opening input socket...")
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", self.remote_port_if_needed))
            server.listen()
            self.running_remote = True
        except Exception as e:
            print(f"Failed to start input server: {e}")
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

    def local_choice_loop(self):
        self.t0_identity_run = time.time()
        while True:
            print(f"{self.ordered_context}")
            for vla_complex in self.vla_complexes:
                print(f"____{vla_complex.tool_name}____")
                print(f"{inspect.signature(vla_complex.execute)}")
                choice = input(f"(\"\" to skip): ")
                if not choice == "":
                    args = []
                    parameters = {}
                    for arg in list(inspect.signature(vla_complex.execute).parameters.keys()):
                        value = input(f"\t{arg}: ")
                        args.append(value)
                        parameters[arg] = value
                    self.execute_vla_complex(vla_complex, *args)
                    self.write_output(ToolChoiceMade(
                        function={
                            "name": vla_complex.tool_name,
                            "description": vla_complex.execute.__doc__,
                            "parameters": parameters
                        }
                    ), {
                        "model": None,
                        "source": "human",
                        "latency": time.time() - self.t0_identity_run
                    })
                    return args
                else:
                    print(f"_______")
            print(f"\nV V V V V\n")

    def remote_choice_loop(self): 
        choice_data = self.choice_data()
        self.send_q.put(choice_data)
        print("Choice data on send queue.")
        self.t0_identity_run = time.time()

    def respond_loop(self, stop_event):
        try:
            while not stop_event.is_set():
                msg = self.inbound_q.get()
                choice = json.loads(msg)

                tool_name = choice[0]
                args = choice[1:]
                vlac = self.vla_complex_by_name(tool_name)
                self.execute_vla_complex(vlac, *args)
                bound = inspect.signature(vlac.execute).bind(*args)
                bound.apply_defaults()
                parameters = dict(bound.arguments)
                self.write_output(ToolChoiceMade(
                    function={
                        "name": vlac.tool_name,
                        "description": vlac.execute.__doc__,
                        "parameters": parameters
                    }
                ), {
                    "model": None,
                    "source": "human",
                    "latency": time.time() - self.t0_identity_run
                })
        except Exception as e:
            print(f"Error in respond loop!: {e}")

    def choice_data(self) -> ChoiceData:
        """
        returns just the data necessary to make a choice
        """
        c = ChoiceData(context=str(self.ordered_context))
        for vla_complex in self.vla_complexes:
            stripped = VLA_ComplexStripped(
                vla_complex.tool_name,
                signature = self.signature_dict(vla_complex.execute)
            )
            c.vla_complexes.append(stripped)
        return c

    def signature_dict(self, func):
        sig = inspect.signature(func)
        result = {}
        for name, param in sig.parameters.items():
            annotation = param.annotation

            if annotation is inspect._empty:
                type_name = "Any"
            else:
                # If it's a type, get its name
                if hasattr(annotation, "__name__"):
                    type_name = annotation.__name__
                else:
                    # For typing types like List[int], Optional[str], etc.
                    type_name = str(annotation)

            result[name] = type_name
        return result

    def send_loop(self, sock: socket.socket, stop_event):
        print("send_loop on")
        try:
            while not stop_event.is_set():
                choice_data = self.send_q.get()
                #print(f"Got choice data {choice_data}")
                payload_dict = asdict(choice_data)
                msg = json.dumps(payload_dict)
                sock.sendall((msg + "\n").encode("utf-8"))

        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            stop_event.set()

    

    def recv_choice(self, sock: socket.socket):
        """
        Receives tool_name and args
        """
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
                msg = self.recv_choice(sock)
                if msg is None:
                    break
                self.inbound_q.put(msg)
        except (ConnectionResetError, OSError):
            pass
        finally:
            stop_event.set()

    

    def execute_vla_complex(self, vla_complex, *instruction):
        asyncio.run(vla_complex.execute(*instruction))

from one_identity_at_a_time import SingleIdentityRunningLock

class OrderedContextLLMAgent(OrderedContextAgent):
    instructions: str
    goal: Optional[str]
    model_name: str
    identity: Agent
    identity_lock: SingleIdentityRunningLock

    def __init__(self, name: str, instruction: str, goal: Optional[str] = None):
        super().__init__(name)
        self.instructions = instruction
        self.goal = goal

        self.model_name="o4-mini"
        self.identity_lock = SingleIdentityRunningLock()

        self.metrics = metrics.Profile(name)

    def assemble_context(self):
        self.context_init() # may be summarized or not
        self.order_context()

    async def request(self):
        print(f"Agent requested...")
        
        try:
            async with self.identity_lock:
                if self.whether_to_summarize():
                    ss = await self.summarize_states()
                    self.update_states_with_summarization(ss)
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
            model=self.model_name
        )

    async def run_the_identity(self):
        try:
            context = str(self.ordered_context)
            print(f"___Prompt__\n{context}")
            self.write()
            result = await Runner.run(self.identity, context, max_turns=3)
            self.write_output(result, {
                "model": self.model_name,
                "name": self.name,
                "latency": time.time() - self.t0_identity_run
            })
            self.metrics.add_model_usage(result.context_wrapper.usage, self.model_name)
        except Exception as e:
            print(f"Wish I could cancel: {e}")
            return "This task is trash"

    def instance_system_prompt(self):
        system_prompt = self.instructions
        if self.goal:
            system_prompt += self.goal
        self.system = system_prompt
        return system_prompt