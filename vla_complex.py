
from gda import GDA
from vla import VLA
from vlm import VLM
import time
from typing import List, Any, Callable
from signals import DONE
from signals import CONTINUE, RERUN
import os
from datetime import datetime
import threading
import asyncio

from displays import log, timestamp, update_activity

RAW_EXECUTE = False
EXECUTE = True

from exceptions import Shutdown

global runner
runner: Callable = None

class VLA_Complex:
    # Everything that's treated the same by a GDA
    # [TODO] Need to provide dictionary for multiple different VLAs.
    tool_name: str
    def __init__(self, vla: Any, capability_desc: str, tool_name: str, on_start=False):
        self.vla = vla
        self.execute.__func__.__doc__ = capability_desc
        self.parent = None
        
        self.last_instruction = None
        
        self.tool_name = tool_name
        self.on_start = on_start
        self.use_frequency = 0.0

    async def execute(self, instruction: str):
        """___________________________"""
        self.use_frequency += 1
        if not self.parent:
            raise Exception(f"{self.tool_name} has not properly been linked to an agent.")
        instruction_print = f"...{instruction[-20:]}" if len(instruction) > 20 else instruction
        log(f"\t{self.parent.name} >>> {self.tool_name}(\"{instruction_print}\")", self.parent)
        if not self.parent.applicable:
            log(f"{self.parent.name} call to {self.tool_name} is inapplicable ", self.parent)
            log(f"{self.parent.name} call is inapplicable ", self)
            return f"Inapplicable call. Please finish execution (no final response needed)."  
        log(f"LLM >>> {self.tool_name}(\"{instruction_print}\")", self)
        
import json
class DrawOnBlackboard(VLA_Complex):
    def __init__(self):
        super().__init__(self.draw, "Write text to a blackboard. Use for making plans, and taking notes about the environment (calling only once). This is a mnemonic device. You can use it to make your thinking available to other versions of yourself at other times, or fore transparently sharing plans with the user. The `str_dict` arg will replace the entire blackboard. Pass empty string to give no updates and just view.", "draw_on_blackboard")
        self.blackboard = {}
    def __str__(self):
        return f"DrawOnBlackBoard"
    
    async def execute(self, str_dict: str=""):
        await super().execute(str_dict)
        try:
            return self.vla(str_dict=str_dict)
        except Exception:
            log(f"Failed to start `draw` method.", self)
        

    def draw(self, str_dict: str):
        global runner
        if str_dict == "":
            rerun_input = self.blackboard 
            
            runner(rerun_input, str(self))
            return "Success. Return immediately."
        try:
            bb_dict = json.loads(str_dict)
            self.blackboard.update(bb_dict)
            
        except Exception:
            dict_print = f"...{str_dict[-20:]}" if len(str_dict) > 20 else str_dict

            log(f"{dict_print} is not JSON-loadable...", self)
            try:   
                self.blackboard["Blackboard"] = str_dict
            except Exception as e:
                return f"Failed to modify blackboard: {e}."
            
            self.blackboard["Timestamp"] = timestamp()
            log(f"Blackboard updated to:\n{self.blackboard}", self)
            rerun_input = self.blackboard 
            
            runner(rerun_input, str(self))
            return "Added to blackboard. Return immediately."
        
class Logger(VLA_Complex):
    def __init__(self):
        super().__init__(log, "Print/log a message, which the programmer may or may not choose to view. Can be called before other more serious functions.", "log")

    async def execute(self, text: str):
        await super().execute(text)

        self.vla(text=text)
        return "added to logs*"

    def log(self, text: str):
        log(f"\"{text}\"", self)


class Chat(VLA_Complex):
    parent: GDA
    
    def __init__(self):
        super().__init__(self.respond, "Say something directly to user. Do NOT use this for planning, only for informal conversation.", "chat", True)
        
        ### State ###
        self.long_term_memory = None
        self.session = None

        ### Threads ###
        self.listener = threading.Thread(target=self.listen, daemon=True)
        self.listening = False

        # Signal like
        self.user_input = ""

    def _repr__(self):
        return f"Chat repr"

    def __str__(self):
        return f"Chat"
    
    async def execute(self, text: str):
        await super().execute(text)

        log(f"\tCalling vla {self.vla.__name__}...", self)
        self.vla(text=text)

        
        if self.long_term_memory is None:
            self.long_term_memory = []
        if self.session is None:
            self.session = []
        if not self.listening:
            self.listening = True
            self.listener.start()

        self.session.append({f"{timestamp()} Me (robot)": f"{text}"})
        
        log("\tExecute process done", self)

    async def start(self, rerun_function: Callable):
        global runner
        if runner is None:
            runner = rerun_function
        try:
            await self.execute("Hello?")
        except Shutdown:
            print(f"\nSystem shutting down...")
            raise Shutdown()

    def listen(self):
        try:
            while self.listening:
                update_activity("Listening...", self)
                self.user_input = input("V\tV\tV Give prompt: V\tV\tV\n")
                print("\t\t________________\n")
                rerun_input = {
                        "Long term memory": self.long_term_memory,
                        "Session information": self.session.copy()
                    }
                if self.user_input == "":
                    log(f"{self.tool_name} >>> LLM: ...no new signal...", self)
                else:
                    rerun_input["Current user message"] = self.user_input
                    log(f"{self.tool_name} >>> LLM: {rerun_input}", self)
                    self.session.append({f"{timestamp()} User":f"{self.user_input}"})
                
                global runner
                runner(rerun_input, str(self))
        except Shutdown:
            print("Shutdown at listen")
            print(f"\t\tClosing.")
            raise Shutdown("Shutting down.")

    def respond(self, text: str):
        log("\t\tExecute process done", self)
        print(f"\nRobot: {text}")


class EpisodicRecorder(VLA_Complex):
    """
    Input:
        Terminal IO and ^C
    Checking signal:
        CONTINUE, DONE
    Running signal:behavior tree
        RUNNING_LOOP: bool
        RUNNING_E: bool
        task: str
    """


    def __init__(self, dataset_recorder_caller, tool_name):
        self.record = dataset_recorder_caller
        super().__init__(signal, "Task", tool_name)

    async def execute(self, instruction):
        await super().execute(instruction)
        check, task_name = "CONTINUE", instruction
        
        while check == "CONTINUE":
            try:
                self.vla(signal={"RUNNING_LOOP": True, "RUNNING_E": True, "task": task_name})
                while True:
                    pass
            except KeyboardInterrupt:
                self.vla(signal={"RUNNING_LOOP": True, "RUNNING_E": False, "task": ""})
                try:
                    check, new_task_name = self.parent.check("EXIT_E")
                    if new_task_name == "":
                        continue
                    else:
                        task_name = new_task_name
                        self.vla(signal={"RUNNING_LOOP": True, "RUNNING_E": True, "task": task_name})
                except KeyboardInterrupt:
                    self.vla(signal={"RUNNING_LOOP": False, "RUNNING_E": False, "task": ""})
                    check, dataset_name = self.parent.check("EXIT_LOOP")
                    self.vla(signal={"RUNNING_LOOP": False, "RUNNING_E": False, "dataset_name": dataset_name})
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
        super().__init__(self.vla, capability_desc, tool_name)
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
                self.vla({"instruction": instruction, "flag": "GO"})
            #print(f"\t\tAfter executing \"{instruction}\"")
            t = time.time()
            await asyncio.sleep(self.monitor_sleep_period)
            self.last_instruction = instruction
            self.execution_cache.extend([instruction, time.time() - t])

            monitor_prompt = f"Can we continue to \"{instruction}\"? (OK | ... | DONE)"

            status = self.watcher.status_sync(monitor_prompt) # Continuer

            if status == DONE:
                log(f"\t\tDone with \"{instruction}\"", self)
                self.vla({"instruction": instruction, "flag": "STOP"})
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
        super().__init__(vla, capability_desc, tool_name)

        ### State
        self.long_term_memory = None
        self.session = None
        
        ### Signal
        self.signal = {"flag": ""}

        ### Threads
        # Internal to planner

    async def execute(self, destination: str):
        try:
            await super().execute(destination)
        except Exception as e:
            print(f"Could not call super's execute: {e}")
            log(f"Could not call super's execute: {e}", self) 
        if self.long_term_memory is None:
            self.long_term_memory = []

        if self.session is None:
            self.session = []

        # Process signal
        if destination == "STOP":
            self.signal["flag"] = "STOP"
            self.signal["goal"] = "empty"
        else:
            self.signal["flag"] = CONTINUE
            self.signal["goal"] = destination

        try:
            log(f"\tDispatching VLA with signal: \"{self.signal}\"", self)
            self.vla(self.signal)
            log(f"\tAfter instructing \"{destination}\" ", self)
            log(f"\tSignal after: {self.signal}", self)
            if destination == self.last_instruction:
                return f"Try again. You're either already pathing there (no need to call this tool), or you've already arrived."
            if self.signal["flag"] == DONE:
                rerun_input = self.get_rerun_input(f"Arrived at {self.signal["goal"]}.")
                check = await self.parent.check(rerun_input)
                if check == "RERUN":
                    return f"Successfully arrived at {destination}. Return immediately with no output."
            if self.signal["flag"] == "STOP":
                return f"Stopped."
            else:
                self.session.append(f"Followed instruction to {self.signal['goal']}")
            #await asyncio.sleep(0.5)
            #print(f"After awaiting")
        except Exception as e:
            print(f"!!{e}!!")
            return f"Planning failed. Make sure to pass a destination from {self.vla.destinations} (or STOP), and nothing more."
        log("Done with execute process", self)

            # Status = OK, Check = CONTINUE
    
    def get_rerun_input(self,status=None):
        if status is None:
            status = f"{len(self.vla.path.nodes)} waypoints left in path to {self.signal['goal']}. Travel time: {self.vla.travel_time}"
        rerun_input = {
            "Long term memory": self.long_term_memory,
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