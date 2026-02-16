
from vla import VLA
from vlm import VLM
import time
from typing import List, Any, Callable

import os
from datetime import datetime
import threading
import asyncio
import socket
from displays import log, timestamp, update_activity
import queue
from chat_utils import recv_line, recv_loop, send_loop
import scheduler 

from exceptions import Shutdown

runner: Callable = None

import vla_complex_state

class VLA_Complex:
    tool_name: str
    def __init__(self, vla: Any, capability_desc: str, tool_name: str, on_start=False):
        self.vla = vla
        self.capability_desc = capability_desc
        self.update_docstring(capability_desc)
        
        
        self.tool_name = tool_name
        self.on_start = on_start
        self.use_frequency = 0.0

        self.name_in_session = tool_name
        self.name_in_impression = tool_name

    def update_docstring(self, new_capability_desc: str):
        self.execute.__func__.__doc__ = new_capability_desc

    async def execute(self, instruction: str):
        """___________________________"""
        self.use_frequency += 1
        instruction_print = f"...{instruction[-30:]}" if len(instruction) > 20 else instruction
        log(f"LLM >>> {self.tool_name}(\"{instruction_print}\")", self)

    def rerun_agent(self):
        global runner
        if runner:
            runner(str(self))
        else:
            raise Exception("Why is there no runner function?")

class Scheduler(VLA_Complex):
    def __init__(self):
        super().__init__(self.make_schedule, "Use to prompt a scheduler component that will stimulate you with the proper things to do at the right time. If you already have a schedule, calling this will show your schedule. \nArgs: `input` - a description of the time period over which to schedule, and the contents of the schedule.", "make_schedule")
        self.on_schedule = False
        self.state = vla_complex_state.State(impression=None)

    async def execute(self, input: str):
        global runner
        if self.on_schedule:
            return f"The schedule you automatically follow:\n{scheduler.schedule_blocks}"
        else:
            print(f"\nSetting {scheduler.notify} to {runner.__name__}")
            scheduler.notify = runner
            # the following shouldn't be blocking but it is.
            await self.vla(input)
            self.state.impression = scheduler.raw_str
            self.on_schedule = True
            return "Schedule set. Return immediately."    

    def pull_state(self):
        return_ = {
            "Schedule (python code that runs prompts you)": self.state.impression.copy()
        }
        return return_

    async def make_schedule(self, input):
        
        await scheduler.make_schedule(input)
        print(f"Back from making schedule. Running... {scheduler.schedule_blocks}")
        threading.Thread(target=scheduler.run_schedule, daemon=True).start()
        print(f"Done starting schedule!")

import json
class BlackBoard(VLA_Complex):
    def __init__(self, name):
        super().__init__(self.draw, "Write text to memory. Use for making plans, and taking notes about the environment. The `str_dict` arg will replace the entire blackboard. Pass empty string to give no updates and just view.", name)
        self.state = vla_complex_state.State(impression={})
        self.rerunning_from_blackboard_update = False

    def __str__(self):
        return f"DrawOnBlackBoard"
    
    async def execute(self, str_dict: str=""):
        await super().execute(str_dict)
        if not self.rerunning_from_blackboard_update:
            threading.Thread(target=self.run_watch_blackboard, daemon=True).start()
        try:
            return self.vla(str_dict=str_dict)
        except Exception:
            log(f"Failed to start `draw` method.", self)

    def run_watch_blackboard(self):
        while True:
            last_blackboard = self.state.impression.copy()
            time.sleep(1)
            if not last_blackboard == self.state.impression:
                self.rerun_agent()

    def draw(self, str_dict: str):
        global runner
        if str_dict == "":            
            return "Success. Return immediately."
        try:
            bb_dict = json.loads(str_dict)
            self.state.impression.update(bb_dict)
        except Exception:
            dict_print = f"...{str_dict[-20:]}" if len(str_dict) > 20 else str_dict
            log(f"{dict_print} is not JSON-loadable...", self)
            try:   
                self.state.impression["Blackboard"] = str_dict
            except Exception as e:
                return f"Failed to modify blackboard: {e}."
            self.state.impression["Timestamp"] = timestamp()
            log(f"Blackboard updated to:\n{self.blackboard}", self)            
            return "Added to memory. Return immediately."
        
class Logger(VLA_Complex):
    def __init__(self):
        super().__init__(log, "Print/log a message, which the programmer may or may not choose to view. Can be called before other more serious functions.", "log")
        self.state = vla_complex_state.State(session=[])

    async def execute(self, text: str):
        await super().execute(text)
        self.vla(text=text)
        self.state.add_to_session("logged", text)
        return "Success. Return immediately."

    def log(self, text: str):
        log(f"\"{text}\"", self)


class Chat(VLA_Complex):    
    def __init__(self, tool_name="chat", tool_description="Say something directly to user. Use this for informal realistic conversation. Be as realistic as you can, no monologues/paragraphs.", chat_port=5001):
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
            threading.Thread(target=self.run_server, daemon=True).start()
        await super().execute(text)
        self.vla(text)
        self.state.add_to_session("self", text)
        return "Message sent. Return immediately."
        
    def run_server(self):
        print("Opening socket...")
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", self.chat_port))
            server.listen()
            self.listening = True
        except Exception as e:
            print(f"Failed to start chat server: {e}")
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
        return self.state

    def restore(self):
        """
        Should address the change in state after sending a context
        """
        pass

    def respond(self, user_input):
        print(f"Message {user_input} received...")
        self.state.add_to_session("Message", user_input)
        self.state.impression = {"Current user message":f"{user_input}"}
        self.rerun_agent()

    async def start(self, rerun_function: Callable):
        print(f"In Chat start(). Setting rerun_function to {rerun_function}")
        if not self.listening:
            threading.Thread(target=self.run_server, daemon=True).start()
        global runner
        if runner is None:
            runner = rerun_function
        try:
            self.reply("")
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
        self.signal:dict={"RUNNING_LOOP":True, "RUNNING_E": True, "task":"Put the cube in the first aid kit"}
        # signal at first blocks episode loop, waiting for "go" from teleop
        self.state = vla_complex_state.State(session=[])

    async def execute(self, instruction: str):
        await super().execute(instruction)
        if not self.running:
            threading.Thread(target=self.interaction_runner.run, args=(self.signal,), daemon=True).start()
        if instruction == "STOP":
            self.signal["RUNNING_E"] = False
        else:
            self.signal["task"] = instruction
        print("Action applied. Return immediately.")


class EpisodicRecorder(VLA_Complex):
    """
j
    """
    def __init__(self, interaction_runner, tool_name):
        self.interaction_runner = interaction_runner
        super().__init__(None, "does a thing", tool_name)
        self.running = False
        self.conducting = False
        # instantiates signal to coordinate monitors with runner (both are in the runner)
        self.signal:dict={"RUNNING_LOOP":False, "RUNNING_E": True, "task":"Put the cube in the first aid kit"}
        if interaction_runner.demoed:
            self.signal["DECISION"] = None
        # signal at first blocks episode loop, waiting for "go" from teleop
        self.state = vla_complex_state.State(session=[])

    async def execute(self, instruction: str):
        await super().execute(instruction)
        self.signal["task"] = instruction
        self.signal["RUNNING_LOOP"] = True
        print(f"Changed signal to {self.signal}")
        if not self.running:
            threading.Thread(target=self.interaction_runner.run, args=(self.signal,), daemon=True).start()
            self.running = True
        print("Success. Return immediately.")

    """ # Not a starter...
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
    """

class AvaCreateTag(VLA_Complex):
    def __init__(self, base, tool_name: str):
        self.base = base
        self.default_map = 1

        super().__init__(self.create_tag, "Create a new location with the given name at the given coordinates.", tool_name)
        self.state = vla_complex_state.State(session=[])

    async def execute(self, name: str, x: float, y: float, theta: float):
        await super().execute(name)
        self.vla(name, x, y, theta)
        print("Created tag. Return immediately.")

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

class LoadReferences(VLA_Complex):
    def __init__(self, tool_name):
        super().__init__(self.get_junk, "Use to get the state of affairs in your environment.", tool_name)
        self.state = vla_complex_state.State(impression=self.junk)
        
        self.junk = """
Pretend this is useful information.
"""

    def get_junk(self):
        return self.junk


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
        self.state = vla_complex_state.State(session=[])
        self.long_term_memory = []

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
    def pull_state(self):
        state = {
            "Session": self.state.session,
        }
        return state
    
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
        return "Success. Return Immediately."

    # reruns the agent
    def rerun(self, raison):
        rerun_input = {
                "Long term stats": self.long_term_memory,
                "Session information": self.state.session.copy()
            }
        rerun_input["Current drive status"] = raison
        log(f"{self.tool_name} >>> LLM: {rerun_input}", self)
        self.state.session.append({f"{timestamp()} Status":f"{raison}"})

        if runner:
            runner(str(self))

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
        super().__init__(self.act, "Use your arm by either passing PICKUP <name of object> or DROP <null>", tool_name)
        self.listening = False
        self.unity_messages = queue.Queue()
        self.out_messages = queue.Queue()
        self.stop_event = threading.Event()
        ### State ###
        self.state = vla_complex_state.State(session=[], impression={
            "carrying": None,
            "available_objects": None
        })

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
            return f"Picking up {object_name}. Return immediately."
        elif pickup_or_drop == "DROP":
            self.vla("Drop", None)
            self.act("GetAvailableObjects", "null")
            return f"Dropping... Return immediately."
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
                self.state.impression["available_objects"] = content
                if self.state.impression["carrying"]:
                    self.update_docstring(self.capability_desc + json.dumps({"Objects you can pick up after a DROP": self.state.impression["available_objects"]}))
                else:
                    self.update_docstring(self.capability_desc + json.dumps({"Available objects to pick up": self.state.impression["available_objects"]}))
            case "status":
                unity_status = content[0]
                print(f"Status returned {unity_status}")
                if "drop" in unity_status:
                    if self.state.impression["carrying"]:
                        self.state.impression["carrying"] = False
                    self.state.add_to_session("Status", unity_status)
                if "picked up" in unity_status:
                    if not self.state.impression["carrying"]:
                        self.state.impression["carrying"] = unity_status.strip("picked up")
                    self.state.add_to_session("Status", unity_status)
                    self.rerun_agent()
                else:
                    self.state.add_to_session("Status", unity_status)
                    return

#   (no past)/ TS:[-failed to pick up], picked up x, dropped x, failed to pick up y
#                                                   ^          ^           
#                                                 moved      moved
 
    def pull_state(self):
        return self.state

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
        self.state = vla_complex_state.State(session=[], impression={
            "currently travelling": False,
            "current position": "Initial position",
            "destinations": []
        })

        self.unity_functions = None

    def __str__(self):
        return self.tool_name

    async def execute(self, destination: str):
        await super().execute(destination)
        if not self.listening:
            self.start_listener()
        self.vla("SetGoalTo", destination)
        return "Successfully set drive goal. Return immediately."

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

        match type:
            case "destinations":
                self.state.impression["destinations"] = content
                self.update_docstring(self.capability_desc + json.dumps({"Function": "SetGoalTo", "Possible args": self.state.impression["destinations"]}))
            case "functions":
                self.unity_functions = content
                return
            case "status":
                unity_status = content[0]
                if "reached" in unity_status:
                    self.state.add_to_session("Status", unity_status)
                    self.state.impression["current_position"] = unity_status.strip("reached ")
                    self.state.impression["currently_travelling"] = False
                    self.rerun_agent()
                if "goal set" in unity_status:
                    self.state.add_to_session("Status", unity_status)
                    self.state.impression["currently_travelling"] = True
                else:
                    self.rerun_agent()

    def pull_state(self):
        return self.state

    def act(self, unity_callable:str, arg: str):
        
        structure = {"method": unity_callable, "arg":arg}
        self.out_messages.put(json.dumps(structure))

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
# =========================== Tests =========================== #    
