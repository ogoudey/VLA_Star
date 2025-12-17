
from gda import GDA
from vla import VLA
from vlm import VLM
import time
from typing import List, Any
from signals import DONE
from signals import CONTINUE, RERUN
import os
from datetime import datetime
import threading
import asyncio

from logger import log

RAW_EXECUTE = False
EXECUTE = True

class VLA_Complex:
    # Everything that's treated the same by a GDA
    # [TODO] Need to provide dictionary for multiple different VLAs.
    tool_name: str
    def __init__(self, vla_dispatcher: Any, capability_desc: str, tool_name: str, on_start=False):
        self.vla_dispatcher = vla_dispatcher
        self.execute.__func__.__doc__ = capability_desc
        self.parent = None
        
        self.last_instruction = None
        
        self.tool_name = tool_name
        self.on_start = on_start


    async def execute(self, instruction: str):
        """___________________________"""
        if self.parent:
            log(f"{self.parent} called {self.tool_name}", self.parent)
            #if not self.parent.applicable:
            #    return f"Inapplicable call. Please finish execution (no final response needed)."
            
        log(f"Instruction \"{instruction}\" presented to VLA Complex {self.tool_name}", self)

        if self.parent:
            self.parent.applicable = False

class Logger(VLA_Complex):
    def __init__(self):
        super().__init__(lambda text: self.log(text), "Print/log a message, which the programmer may or may not choose to view.", "text")

    async def execute(self, text: str):
        await super().execute(text)

        self.vla_dispatcher(text=text)
        await self.parent.check(f"Just logged '{text}'")

    def log(self, text: str):
        log(f"\"{text}\"", self)


class Chat(VLA_Complex):
    parent: GDA
    def __init__(self):
        super().__init__(lambda text: self.respond(text), "Say `text` to user.", "chat", True)
        
        
        self.long_term_chat_memory = None
        self.session = None

        self.listener = threading.Thread(target=self.listen)
        self.listening = False

        self.user_prompt = {"DONE": False, "Content": ""}

    async def execute(self, text: str):

        await super().execute(text)
        log(f"\tSignal: {{...: {text}}}", self)
        self.vla_dispatcher(text=text)

        if not self.listening:
            self.listener.start()
            self.listening = True
        if self.long_term_chat_memory is None:
            self.long_term_chat_memory = []

        if self.session is None:
            self.session = []

        self.session.append({"Me (robot)": f"{text}"})

        check = "CONTINUE" 
        while check == "CONTINUE":
            log(f"\tIdling before user prompt: \"{self.user_prompt}\"", self)
            while self.user_prompt["DONE"] == False:
                time.sleep(0.1)
                pass
            log(f"\tSensory check received: \"{self.user_prompt}\"", self)
            
            # Construct rerun
            rerun_input = {
                "Long term memory": self.long_term_chat_memory,
                "Session information": self.session,
                "Current user message": self.user_prompt["Content"]
            }
            self.user_prompt["DONE"] = False # ready for new user message
            await self.parent.check(rerun_input, signature=self.tool_name)
            log(f"\tAfter rerun...", self)
            self.session.append({"User":f"{self.user_prompt['Content']}"})
        log("Execute process done", self)

    async def start(self):
        await self.execute("Introduce yourself briefly. (You are chatting to the user.)")

    def listen(self):
        while True:
            self.user_prompt["Content"] = input("V\tV\tV Give prompt: V\tV\tV\n\t")
            print("\t\t________________\n")
            self.user_prompt["DONE"] = True
            while self.user_prompt["DONE"] == True:
                time.sleep(0.1)
                pass

    def respond(self, text: str):
        print(f"\nRobot: {text}")


class EpisodicRecorder(VLA_Complex):
    """
    Input:
        Terminal IO and ^C
    Checking signal:
        CONTINUE, DONE
    Running signal:
        RUNNING_LOOP: bool
        RUNNING_E: bool
        task: str
    """


    def __init__(self, dataset_recorder_caller, tool_name):
        self.record = dataset_recorder_caller
        super().__init__(lambda signal: self.record(signal), "Task", tool_name)

    async def execute(self, instruction):
        await super().execute(instruction)
        check, task_name = "CONTINUE", instruction
        
        while check == "CONTINUE":
            try:
                self.vla_dispatcher(signal={"RUNNING_LOOP": True, "RUNNING_E": True, "task": task_name})
                while True:
                    pass
            except KeyboardInterrupt:
                self.vla_dispatcher(signal={"RUNNING_LOOP": True, "RUNNING_E": False, "task": ""})
                try:
                    check, new_task_name = self.parent.check("EXIT_E")
                    if new_task_name == "":
                        continue
                    else:
                        task_name = new_task_name
                        self.vla_dispatcher(signal={"RUNNING_LOOP": True, "RUNNING_E": True, "task": task_name})
                except KeyboardInterrupt:
                    self.vla_dispatcher(signal={"RUNNING_LOOP": False, "RUNNING_E": False, "task": ""})
                    check, dataset_name = self.parent.check("EXIT_LOOP")
                    self.vla_dispatcher(signal={"RUNNING_LOOP": False, "RUNNING_E": False, "dataset_name": dataset_name})
            break
                
class Single_VLA_w_Watcher(VLA_Complex):
    """
    Checking signal:
        CONTINUE, RERUN, DONE
    Running signal:
        instruction: str
        flag: STOP, GO
    
    """
    def __init__(self, vla: Any, vlm: Any, capability_desc: str, tool_name: str):
        self.vla = vla
        super().__init__(lambda instruction: self.vla(instruction), capability_desc, tool_name)
        self.watcher = vlm

        self.monitor_sleep_period = 2.0
        self.execution_cache_max = 12
        self.execution_cache = []

    async def execute(self, instruction: str):
        await super().execute(instruction)

        monitor_prompt = f"Are we good to {instruction} given that we just did {self.last_instruction}? (OK | ...)" if self.last_instruction else f"Are we good to {instruction}? (OK | ...)"


        status = self.watcher.status_sync(monitor_prompt)
        

        check = await self.parent.check(status) # symbolic check given status
        if check == RERUN: # The parent has reran computation in response to the status
            return f"Done. Call no more tools and return."
        
        ### REAL EXECUTION ###
        self.execution_cache = []
        while check == CONTINUE:
            #print(f"\t\tContinuing to do \"{instruction}\"")
            if EXECUTE:
                self.vla_dispatcher({"instruction": instruction, "flag": "GO"})
            #print(f"\t\tAfter executing \"{instruction}\"")
            t = time.time()
            await asyncio.sleep(self.monitor_sleep_period)
            self.last_instruction = instruction
            self.execution_cache.extend([instruction, time.time() - t])

            monitor_prompt = f"Can we continue to \"{instruction}\"? (OK | ... | DONE)"

            status = self.watcher.status_sync(monitor_prompt) # Continuer

            if status == DONE:
                log(f"\t\tDone with \"{instruction}\"", self)
                self.vla_dispatcher({"instruction": instruction, "flag": "STOP"})
                return "Done"
            
            if status == RERUN: # Address: how would we get here?
                print(f"\t\tWon't continue \"{instruction}\" because \"{status}\"")

            # Status = ... | OK
            check = await self.parent.check(status, self.execution_cache)

            if len(self.execution_cache) > self.execution_cache_max:
                self.execution_cache = []

            if check == RERUN:
                return "Done."
            # Status = OK, Check = CONTINUE

class Navigator(VLA_Complex):
    """
    Running signal:
        goal: str
        flag: CONTINUE, DONE, STOP
    Checking signal:
        RERUN
    """
    def __init__(self, vla: Any, capability_desc: str, tool_name: str):
        self.vla = vla
        super().__init__(lambda instruction: self.vla(instruction), capability_desc, tool_name)
        self.signal = {"flag": ""}
        self.listening = False
        self.long_term_nav_memory = None
        self.session = None
        
    async def execute(self, instruction: str):
        try:
            await super().execute(instruction)
        except Exception as e:
            print(f"Could not call super's execute: {e}")
            log(f"Could not call super's execute: {e}", self) 
        if self.long_term_nav_memory is None:
            self.long_term_nav_memory = []

        if self.session is None:
            self.session = []


        # Process signal
        if instruction == "STOP":
            self.signal["flag"] = "STOP"
            self.signal["goal"] = "empty"
        else:
            self.signal["flag"] = CONTINUE
            self.signal["goal"] = instruction

        try:
            log(f"\tDispatching VLA with signal: \"{self.signal}\"", self)
            self.vla_dispatcher(self.signal)
            log(f"\tAfter instructing \"{instruction}\" ", self)
            log(f"\tSignal after: {self.signal}", self)
            if not instruction == self.last_instruction:
                if self.signal["flag"] == DONE:
                    rerun_input = self.get_rerun_input(f"Arrived at {self.signal["goal"]}.")
                    check = await self.parent.check(rerun_input)
                    if check == "RERUN":
                        return f"Successfully arrived at {instruction}. Return immediately with no output."
                if self.signal["flag"] == "STOP":
                    return f"Stopped."
            #await asyncio.sleep(0.5)
            #print(f"After awaiting")
        except Exception as e:
            print(f"!!{e}!!")
        log("Done with execute process", self)

            # Status = OK, Check = CONTINUE
    
    def get_rerun_input(self,status=None):
        if status is None:
            status = f"{len(self.vla.path.nodes)} waypoints left in path to {self.signal['goal']}"
        rerun_input = {
            "Long term memory": self.long_term_nav_memory,
            "Session information": self.session,
            "Current status": status
        }
        print(f"Input to rerun: {rerun_input}")
        return rerun_input





# Factory
def create_navigator():
    import vla

    VLA = vla.PathFollow()

    return Navigator(VLA, "Plans and executes a path to one of the following landmarks:\n[\"my favorite tree\"]", "navigate")
"""
class Another_TODO:
    # Everything that's treated the same by a GDA
    # [TODO] Need to provide dictionary for multiple different VLAs.
    tool_name: str
    def __init__(self, tool_name: str, parent: GDA, monitors: VLM, vlas: VLA, capability_desc: str):
        self.parent = parent
        self.parent.set_vla_complex(self)
        self.monitor = monitor
        self.vla = vla
        self.execute.__func__.__doc__ = capability_desc

        self.monitor_sleep_period = 2.0
        self.execution_cache_max = 12
        self.execution_cache = []
        self.last_instruction = None
        
        self.tool_name = tool_name

    async def execute(self, instruction: str):
        if not self.parent.applicable:
            return f"Inapplicable call. Please finish execution (no final response needed)."
        print(f"\t\"{instruction}\" presented to VLA Complex")

        if RAW_EXECUTE:
            self.vla(instruction)
            return f"Done. Call no more tools and return."


        self.parent.applicable = False
        monitor_prompt = f"Are we good to {instruction} given that we just did {self.last_instruction}? (OK | ...)" if self.last_instruction else f"Are we good to {instruction}? (OK | ...)"

        recommendor_prompt = f"What action shall we take in order to {self.parent.overhead_prompt}"


        status = self.monitor.status_sync(monitor_prompt) # Continuer
        


        # Just a monitor's status
        #status = self.monitor.status(vlm_prompt) # Starter
        
        
        
        
        check = await self.parent.check(status)
        if check == RERUN:
            return f"Done. Call no more tools and return."
        self.execution_cache = []
        while check == CONTINUE:
            print(f"\t\tContinuing to do \"{instruction}\"")
            if EXECUTE:
                self.vla({"instruction": instruction, "flag": "GO"})
            print(f"\t\tAfter executing \"{instruction}\"")
            t = time.time()
            await asyncio.sleep(self.monitor_sleep_period)
            self.last_instruction = instruction
            self.execution_cache.extend([instruction, time.time() - t])

            monitor_prompt = f"Can we continue to \"{instruction}\"? (OK | ... | DONE)"

            if USE_RECOMMENDER:
                taskA = asyncio.create_task(self.monitor.status(monitor_prompt))
                taskB = asyncio.create_task(self.monitor.recommendation(recommendor_prompt))

            # Wait for both to finish and get results
                status, recommendation = await asyncio.gather(taskA, taskB)
            else:
                status = self.monitor.status_sync(monitor_prompt) # Continuer
                recommendation = None

            if status == DONE:
                print(f"\t\tDone with \"{instruction}\"")
                self.vla({"instruction": instruction, "flag": "STOP"})
                return "Done"
            
            if status == RERUN:
                print(f"\t\tWon't continue \"{instruction}\" because \"{status}\"")

            check = await self.parent.check(status, recommendation, self.execution_cache) # Don't print after this
            if len(self.execution_cache) > self.execution_cache_max:
                self.execution_cache = []
            if check == RERUN:
                return "Done."
            
            #print(self.execution_cache)
            
            
                #self.execution_cache.pop(0)
                #self.execution_cache.pop(0)
                #print(f"Forgetting... -> ", self.execution_cache)
"""