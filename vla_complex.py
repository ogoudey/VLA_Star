
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
import socket
from displays import log, timestamp, update_activity
import queue

from chat_utils import recv_line, recv_loop, send_loop
import scheduler 

RAW_EXECUTE = False
EXECUTE = True

from exceptions import Shutdown

global runner
runner: Callable = None

any_applicable = True
class ExecuteLocked(Exception):
    pass

import vla_complex_state
class VLA_Complex:
    # Everything that's treated the same by a GDA
    # [TODO] Need to provide dictionary for multiple different VLAs.
    tool_name: str
    def __init__(self, vla: Any, capability_desc: str, tool_name: str, on_start=False):
        self.vla = vla
        self.capability_desc = capability_desc
        self.update_docstring(capability_desc)
        self.parent = None
        
        self.last_instruction = None
        
        self.tool_name = tool_name
        self.on_start = on_start
        self.use_frequency = 0.0

        self.name_in_session = tool_name
        self.name_in_impresssion = tool_name

    def update_docstring(self, new_capability_desc: str):
        self.execute.__func__.__doc__ = new_capability_desc

    async def execute(self, instruction: str):
        """___________________________"""
        if not any_applicable:
            raise ExecuteLocked("Not applicable!")
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

class Scheduler(VLA_Complex):
    def __init__(self):
        super().__init__(self.make_schedule, "Use to prompt a scheduler component that will stimulate you with the proper things to do at the right time. If you already have a schedule, calling this will show your schedule. \nArgs: `input` - a description of the time period over which to schedule, and the contents of the schedule.", "make_schedule")
        self.on_schedule = False
        self.state = vla_complex_state.State()

    async def execute(self, input: str):
        global runner
        if self.on_schedule:

            return f"The schedule you automatically follow:\n{scheduler.schedule_blocks}"
            
        else:
            print(f"\nSetting {scheduler.notify} to {runner.__name__}")
            scheduler.notify = runner
            # the following shouldn't be blocking but it is.
            await self.vla(input)
            self.on_schedule = True
            return "You are on schedule. Return immediately (no further action required)."
    
    def recede(self):
        """
        Shoudl address any changes needed after rerun-request
        """  
        pass     

    def pull_state(self):
        state = {
            "Schedule (python code that runs prompts you)": self.state.impression.copy()
        }
        self.restore() # 
        return state

    def restore(self):
        """
        Should address the change in state after sending a context
        """
        pass

    async def make_schedule(self, input):
        
        await scheduler.make_schedule(input)
        print(f"Back from making schedule. Running... {scheduler.schedule_blocks}")
        threading.Thread(target=scheduler.run_schedule, daemon=True).start()
        self.state.impression = scheduler.schedule_blocks
        print(f"Done starting schedule!")

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
    
    def __init__(self, tool_name="chat", tool_description="Say something directly to user. Do NOT use this for planning, only for informal conversation.", chat_port=5001):
        super().__init__(self.reply, tool_description, tool_name, True)
        print(f"Created {tool_name} port on {chat_port}")
        self.chat_port = chat_port


        ### State ###
        self.state = vla_complex_state.State(session=[])

        ### Threads ###
        self.listening = False

        self.send_q = queue.Queue()
        self.inbound_q = queue.Queue()

    def _repr__(self):
        return f"Chat repr"

    def __str__(self):
        return f"{self.tool_name}"

    async def execute(self, text: str):
        if not self.listening:
            ### Starts runner (thread)
            threading.Thread(target=self.run_server, daemon=True).start()

        await super().execute(text)
         
        self.vla(text)

        self.state.add_to_session({f"{timestamp()} Me (robot)": f"{text}"})
        

    def run_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", self.chat_port))
        server.listen()
        self.listening = True
        print("Chat server waiting...")
        update_activity("Chat server waiting...", self.tool_name)
        while self.listening:
            client_sock, addr = server.accept()
            print("Client connected:", addr)
            threading.Thread(
                target=self.handle_client,
                args=(client_sock,),
                daemon=True
            ).start()

    def handle_client(self, sock):
        stop_event = threading.Event()
        

        threading.Thread(
            target=recv_loop,
            args=(sock, self.inbound_q, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=send_loop,
            args=(sock, self.send_q, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=self.respond_loop,
            args=(stop_event,),
            daemon=True
        ).start()

        update_activity("Listening...", self.tool_name)
        try:
            while not stop_event.is_set():
                time.sleep(1)
        finally:
            update_activity("Stopping listening...", self.tool_name)
            stop_event.set()
            sock.close()

    def respond_loop(self, stop_event):
        while not stop_event.is_set():
            msg = self.inbound_q.get()
            self.respond(f"{msg}")
            self.recede()

    def recede(self):
        """
        Shoudl address any changes needed after rerun-request
        """  
        pass     

    def pull_state(self):
        state = {
            "Session": self.state.session.copy()
        }
        self.restore() # 
        return state

    def restore(self):
        """
        Should address the change in state after sending a context
        """
        pass

    def respond(self, user_input):
        
        rerun_input = {
                "Long term memory": self.long_term_memory,
                "Session information": self.session.copy()
            }
        
        if user_input == "":
            log(f"{self.tool_name} >>> LLM: ...no new signal...", self)
        else:
            rerun_input["Current message"] = user_input
            log(f"{self.tool_name} >>> LLM: {rerun_input}", self)
            self.session.append({f"{timestamp()} Message":f"{user_input}"})

        global runner
        if runner:
            runner(rerun_input, str(self))
        else:
            raise Exception("Why is there no runner function?")

    async def start(self, rerun_function: Callable):
        print(f"In Chat start()...")
        global runner
        if runner is None:
            runner = rerun_function
        try:
            await self.execute("...")
        except Shutdown:
            print(f"\nSystem shutting down...")
            raise Shutdown()

    
    def reply(self, message: str):
        self.send_q.put(message)


    

class VLA_Tester(VLA_Complex):
    def __init__(self, interaction_runner, tool_name):
        self.interaction_runner = interaction_runner
        super().__init__(None, "does a thing", tool_name)
        self.running = False

        # instantiates signal to coordinate monitors with runner (both are in the runner)
        self.signal:dict={"RUNNING_LOOP":True, "RUNNING_E": False, "task":"Put the cube in the first aid kit"}
        # signal at first blocks episode loop, waiting for "go" from teleop

    async def execute(self, instruction: str):
        await super().execute(instruction)
        if not self.running:
            threading.Thread(target=self.interaction_runner.run, args=(self.signal,), daemon=True).start()
        if instruction == "STOP":
            self.signal["RUNNING_E"] = False
        else:
            self.signal["task"] = instruction


class EpisodicRecorder(VLA_Complex):
    """
j
    """


    def __init__(self, interaction_runner, tool_name):
        self.interaction_runner = interaction_runner
        super().__init__(None, "does a thing", tool_name)
        self.running = False

        # instantiates signal to coordinate monitors with runner (both are in the runner)
        self.signal:dict={"RUNNING_LOOP":True, "RUNNING_E": False, "task":"Put the cube in the first aid kit"}
        # signal at first blocks episode loop, waiting for "go" from teleop

    async def execute(self, instruction: str):
        await super().execute(instruction)
        if not self.running:
            threading.Thread(target=self.interaction_runner.run, args=(self.signal,), daemon=True).start()
                
    async def start(self, rerun_function: Callable):
        print(f"In EpisodicRecorder start()...")
        global runner
        if runner is None:
            runner = rerun_function
        try:
            await self.execute("Default Task please")
        except Shutdown:
            print(f"\nSystem shutting down...")
            raise Shutdown()

class AvaCreateTag(VLA_Complex):
    def __init__(self, base, tool_name: str):
        self.base = base
        self.default_map = 1

        super().__init__(self.create_tag, "Create a new location with the given name at the given coordinates.", tool_name)

    async def execute(self, name: str, x: float, y: float, theta: float):
        await super().execute(name)
        self.vla(name, x, y, theta)

    def add_to_context(self):
        data = self.base.get_position()["data"]
        return {
            "Current position": {
                "x": data["x"],
                "y": data["y"],
                "theta": data["theta"],
            },
            "A point 0.5 meters forward": [
                self.base.get_point_forward_d(0.5)
            ],
            "Note": "+theta is counterclockwise from above"
            
        }

    def create_tag(self, name, x, y, theta):
        self.base.create_tag(self.default_map, name, x, y, theta)

class AvaDrive(VLA_Complex):
    # A VLA Complex

    # is initialized in the factory
    def __init__(self, base, tool_name: str):
        self.base = base
        self.default_map = 1
        

        super().__init__(self.drive, "Drive to a location in the real world. Location must be one of the ones given, or STOP to stop moving.", tool_name)
        self.drive_updates_on = False
        self.driving = False

        ### State ###
        self.long_term_memory = []
        self.session = []
        
        self.locations_to_tagIds = dict()
        self.refresh_locations()

    # has a primary "act" method
    def drive(self, location: str):
        print(f"Drive on {location}")
        if location == "Dock":
            self.base.smart_dock()
        elif location == "STOP":
            self.base.stop_robot()
        else:
            try:
                print(f"Driving to {self.locations_to_tagIds[location]} on map {self.default_map}")
                self.base.drive_to_tag(self.default_map, self.locations_to_tagIds[location])
            except Exception:
                return (f"Failed to drive to the location. Make sure {location} is one from {list(self.locations_to_tagIds.keys())}, or Dock or STOP")

    # adds to uniform context
    def add_to_context(self):
        self.refresh_locations()
        return {
            "Known locations": list(self.locations_to_tagIds.keys())
        }
    
    # often has ongoing threads
    def run_drive_updates_client(self):

        while True:
            while self.driving:
                drive_updates = self.base.drive_updates()["data"]["status"] # good for now
                if "COMPLETE" in drive_updates.values():
                    self.rerun("Destination reached.")
                    self.driving = False
            time.sleep(1)

    # is called by an agent, with args. (This call must be non-blocking)
    async def execute(self, location: str):
        print("Ava Drive called.")
        await super().execute(location)
        if not self.drive_updates_on:
            threading.Thread(target=self.run_drive_updates_client).start()
        self.vla(location)
        self.driving = True

    # reruns the agent
    def rerun(self, raison):
        rerun_input = {
                "Long term stats": self.long_term_memory,
                "Session information": self.session.copy()
            }        
        rerun_input["Current drive status"] = raison
        log(f"{self.tool_name} >>> LLM: {rerun_input}", self)
        self.session.append({f"{timestamp()} Status":f"{raison}"})

        if runner:
            runner(rerun_input, str(self))

    def refresh_locations(self):
        tags_data = self.base.list_tags(self.default_map)["data"]
        self.base.pp(tags_data)
        tags_info = tags_data["tags"]

        for id, tag_info in tags_info.items():
            if "tracs" in tag_info["attributes"]:
                self.locations_to_tagIds[tag_info["name"]] = tag_info["id"]
"""
Conclusion:
    Out --> drive_to_tag, list_tags()
                              V
    In  <-- drive_updates, list_tags

"""

class UnityArm(VLA_Complex):
    def __init__(self, tool_name):
        super().__init__(self.act, "Use your arm by either passing PICKUP <name of object>", tool_name)
        self.listening = False
        self.unity_messages = queue.Queue()
        self.out_messages = queue.Queue()
        self.stop_event = threading.Event()
        ### State ###
        self.state = vla_complex_state.State(session=[], impression=[])
        
        self.available_objects = []
        self.carrying = None

        self.cycling = False

    def __str__(self):
        return self.tool_name

    async def execute(self, pickup_or_drop: str, object_name: str):
        await super().execute(pickup_or_drop)
        if not self.listening:
            self.start_listener()
        
        if pickup_or_drop == "PICKUP":
            self.vla("PickUp", object_name)
            self.act("GetAvailableObjects", "null")
        elif pickup_or_drop == "DROP":
            self.vla("Drop", None)
            self.act("GetAvailableObjects", "null")
        else:
            return f"Please pass 'PICKUP' or 'DROP', nof {pickup_or_drop}"

    def start_cycling(self):
        threading.Thread(target=self.run_cycle, daemon=True).start()
    
    def run_cycle(self):
        while not self.stop_event.is_set():
            time.sleep(1)
            self.act("GetAvailableObjects", "null")

    def start_listener(self):
        threading.Thread(target=self.run_client, daemon=True).start()

    def recede(self):
        """
        Shoudl address any changes needed after rerun-request
        """  
        pass     

    def pull_state(self):
        state = {
            "Schedule (python code that runs prompts you)": self.state.impression.copy()
        }
        self.restore() # 
        return state

    def restore(self):
        """
        Should address the change in state after sending a context
        """
        pass

    def run_client(self):
        print("Arm listener running")
        print("Arm connecting to Unity...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", 5007))
        self.listening = True
        print("Arm connected to Unity...")
        update_activity("Connected to Unity...", self.tool_name)


        threading.Thread(
            target=recv_loop,
            args=(sock, self.unity_messages, self.stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=send_loop,
            args=(sock, self.out_messages, self.stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=self.react_loop,
            args=(self.stop_event,),
            daemon=True
        ).start()

        update_activity("Listening...", self.tool_name)
        try:
            while self.listening and not self.stop_event.is_set():
                time.sleep(1)
        finally:
            update_activity("Stopping listening...", self.tool_name)
            self.stop_event.set()
            sock.close()

    def react_loop(self, stop_event):
        while not stop_event.is_set():
            msg = self.unity_messages.get()
            self.react(f"{msg}")

    def react(self, unity_message):
        global runner
        # Filter
        # End filter

        # Special messages:

        # HARVEST MESSAGE - ITS A STRING
        unity_message = unity_message.lstrip("\ufeff")  # remove BOM if present
        try:
            structure = json.loads(unity_message)
        except Exception as e:
            return
        try:
            type, content = structure["type"], structure["content"]
        except Exception as e:
            return
        match type:
            case "available_objects":
                self.available_objects = content
                self.update_docstring(self.capability_desc + json.dumps({"Available objects to pick up": self.available_objects}))
                self.state.impression = self.available_objects
            case "status":
                unity_status = content[0]
                print(f"Status returned {unity_status}")
                if not self.enough_context_for_first_rerun():
                    return 
                if "picked up" in unity_status:
                    rerun_input = {
                        "Session information": self.state.session.copy()
                    }
                    log(f"{self.tool_name} >>> LLM: {rerun_input}. Important? {not 'goal set' in unity_status}. Content: {unity_status}", self)    
                    
                    rerun_input["Current status"] = unity_status
                    

                    if runner:
                        runner(rerun_input, self.tool_name)
                    else:
                        raise Exception("Why is there no runner function?")  
                    
                else:
                    self.state.add_to_session({f"{timestamp()} Status":f"{unity_status}"})
                    return

#   (no past)/ TS:[-failed to pick up], picked up x, dropped x, failed to pick up y
#                                                   ^          ^        
#                                                 moved      moved
    def enough_context_for_first_rerun(self):
        return self.available_objects

    def add_to_context(self):
        return {
            "Available objects": self.available_objects,
        }

    # VLA
    def act(self, unity_callable:str, arg: str):
        
        structure = {"method": unity_callable, "arg":arg}
        self.out_messages.put(json.dumps(structure))

    async def start(self, rerun_function: Callable):
        print(f"In UnityArm start()...")
        if not self.listening:
            self.start_listener()
        if not self.cycling:
            self.start_cycling()
        global runner
        if runner is None:
            runner = rerun_function
        try:
            self.act("GetAvailableObjects", "null")
        except Shutdown:
            print(f"\nSystem shutting down...")
            raise Shutdown()
        
class UnityDrive(VLA_Complex):
    def __init__(self, tool_name: str):
        capability_desc = "Provide the function name and the function args. These are Unity functions. Use them to act in the Unity world. Don't assume anything is in the environment that you aren't aware of. Only use functions that are provided. These make real calls and move you - a simulated agent - in Unity."
        super().__init__(self.act, capability_desc, tool_name)
        self.listening = False
        self.unity_messages = queue.Queue()
        self.out_messages = queue.Queue()
        ### State ###
        self.long_term_memory = []
        self.session = []
        
        self.destinations = None
        self.unity_functions = None

    def __str__(self):
        return self.tool_name

    async def execute(self, destination: str):
        await super().execute(destination)
        if not self.listening:
            self.start_listener()
        
        self.vla("SetGoalTo", destination)

    def start_listener(self):
        threading.Thread(target=self.run_client, daemon=True).start()

    def run_client(self):
        print("Listener running")
        print("Connecting to Unity...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", 5006))
        self.listening = True
        print("Connected to Unity...")
        update_activity("Connected to Unity...", self.tool_name)
        
        stop_event = threading.Event()

        threading.Thread(
            target=recv_loop,
            args=(sock, self.unity_messages, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=send_loop,
            args=(sock, self.out_messages, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=self.react_loop,
            args=(stop_event,),
            daemon=True
        ).start()

        update_activity("Listening...", self.tool_name)
        try:
            while self.listening and not stop_event.is_set():
                time.sleep(1)
        finally:
            update_activity("Stopping listening...", self.tool_name)
            stop_event.set()
            sock.close()

    def react_loop(self, stop_event):
        while not stop_event.is_set():
            msg = self.unity_messages.get()
            self.react(f"{msg}")
            

    def react(self, unity_message):
        global runner
        # Filter
        # End filter

        # Special messages:

        # HARVEST MESSAGE - ITS A STRING
        #print(f"Loading {unity_message}!")
        unity_message = unity_message.lstrip("\ufeff")  # remove BOM if present
        try:
            structure = json.loads(unity_message)
        except Exception as e:
            #print(f"Failed to load {unity_message}... {e}")
            return
        try:
            type, content = structure["type"], structure["content"]
        except Exception as e:
            return
        #print(f"Got structure: {structure}")
        #print(f"Matching {type}:")
        match type:
            case "destinations":
                
                if not self.enough_context_for_first_rerun(): # if this is the first time its called
                    self.destinations = content
                    self.update_docstring(self.capability_desc + json.dumps({"Function": "SetGoalTo", "Possible args": self.destinations}))
                    return
                rerun_input = {
                    "Here are the destinations": self.destinations,
                    "Here are the functions to call": self.unity_functions
                    }
                log(f"{self.tool_name} >>> LLM: {rerun_input}", self)
                if runner:
                    runner(rerun_input, str(self))
                else:
                    raise Exception("Why is there no runner function?")
            case "functions":
                self.unity_functions = content
                return
            case "status":
                unity_status = content[0]
                if not self.enough_context_for_first_rerun():
                    return 
                if "goal set" in unity_status:
                    self.session.append({f"{timestamp()} Status":f"{unity_status}"})
                    return
                else:
                    rerun_input = {
                        "Long term memory": self.long_term_memory,
                        "Session information": self.session.copy()
                    }
                    log(f"{self.tool_name} >>> LLM: {rerun_input}. Important? {not 'goal set' in unity_status}. Content: {unity_status}", self)    
                    
                    rerun_input["Current status"] = unity_status
                    

                    if runner:
                        runner(rerun_input, self.tool_name)
                    else:
                        raise Exception("Why is there no runner function?")  
                    
                

    def enough_context_for_first_rerun(self):
        return self.destinations and self.unity_functions

    def add_to_context(self):
        return {
            "Known destinations": self.destinations,
        }

    # VLA
    def act(self, unity_callable:str, arg: str):
        
        structure = {"method": unity_callable, "arg":arg}
        self.out_messages.put(json.dumps(structure))



    # #
    # A. Unity -> Start -> UnityNavigation.start()
    #   
    # B. 
    #   1. start() and in start(), wait for Unity
    #   2. Unity -> Start
    #   
    # C.
    #   1. 
    #   2. Unity -> Start
    #   3. start() -> Unity -> getDestinations/sendDestinations
    #   4. react to destinations
    #
    async def start(self, rerun_function: Callable):
        print(f"In UnityNavigation start()...")
        if not self.listening:
            self.start_listener()
        global runner
        if runner is None:
            runner = rerun_function
        try:
            self.act("GetFunctions", "null")
            self.act("GetDestinations", "null")
        except Shutdown:
            print(f"\nSystem shutting down...")
            raise Shutdown()

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
                rerun_input = self.get_rerun_input(f"Arrived at {self.signal['goal']}.")
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

class Navigator2(VLA_Complex):
    """
    If ONGOING, has at least one thread.
    If ONGOING, may pass a signal to the thread.
    """
    def __init__(self, vla: Any, capability_desc: str, tool_name: str):
        super().__init__(vla, capability_desc, tool_name)

        self.runner = None
        self.running_signal = None

    async def execute(self, instruction):
        """
        Called by agents. Must be non-blocking.
        OPTIONALLY called by start()
        This docstring will be modified.
        """
        await super().execute(instruction)

        any_reason_for_new_navigate, any_reason_to_not_do_new_navigate = True, False
        # e.g. its time to get off the elevator (timed)
        if any_reason_for_new_navigate and not any_reason_to_not_do_new_navigate: # really an unless
            # modify self.runner
            # modify self.running_signal
            pass



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
