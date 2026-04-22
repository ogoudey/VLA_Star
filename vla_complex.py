
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

agent_name: str = None
runner: Callable = None

import vla_complex_state

class VLA_Complex:
    """
    Base class for all modules, VLA_Complexes
    """

    tool_name: str
    def __init__(self, vla: Any, tool_name: str, on_start=False):
        self.vla = vla        
        
        self.tool_name = tool_name
        self.on_start = on_start
        self.use_frequency = 0.0

        self.name_in_session = tool_name
        self.name_in_impression = tool_name

    def update_docstring(self, new_capability_desc: str):
        #### Need to change - must edit universal tool-able form
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
        
    def agent_sleep(self):
        global runner
        runner("STOP")

class Scheduler(VLA_Complex):
    def __init__(self):
        super().__init__(self.make_schedule, "make_schedule")
        self.on_schedule = False
        self.state = vla_complex_state.State(impression=None)

    async def execute(self, input: str):
        """
        Use to prompt a scheduler component that will stimulate you with the proper things to do at the right time. If you already have a schedule, calling this will show your schedule. \nArgs: `input` - a description of the time period over which to schedule, and the contents of the schedule.
        :param input: TODO
        
        """
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
        super().__init__(self.draw, name)
        self.state = vla_complex_state.State(impression={})
        self.rerunning_from_blackboard_update = False

    def __str__(self):
        return f"DrawOnBlackBoard"
    
    async def execute(self, str_dict: str=""):
        """
        Write text to memory. Use for making plans, and taking notes about the environment. The `str_dict` arg will replace the entire blackboard. Pass empty string to give no updates and just view.
        :param str_dict: TODO
        """
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
        super().__init__(log, "log")
        self.state = vla_complex_state.State(session=[])

    async def execute(self, text: str):
        """
        Print/log a message, which the programmer may or may not choose to view. Can be called before other more serious functions.
        :param text: TODO
        """
        await super().execute(text)
        self.vla(text=text)
        self.state.add_to_session("logged", text)
        return "Success. Return immediately."

    def log(self, text: str):
        log(f"\"{text}\"", self)
import signal
import subprocess
from typing import Optional
from general_dataset import SubDataset
from displays import timestamp
import introduction

class Chat(VLA_Complex):
    recorded: bool = False   
    dataset: Optional[SubDataset] = None
    def __init__(self, tool_name="chat", chat_port=5001):
        super().__init__(self.reply, tool_name, True)
        print(f"Creating {tool_name} port on {chat_port}")
        self.chat_port = chat_port
        ### State ###
        self.state = vla_complex_state.State(session=[], impression={})

        ### Threads ###
        self.listening = False

        self.send_q = queue.Queue()
        self.inbound_q = queue.Queue()

    def _repr__(self):
        return f"Chat repr"

    def __str__(self):
        return f"{self.tool_name}"

    async def execute(self, text: str):
        """
        Say something directly to user. Use this for informal realistic conversation. Be as realistic as you can, no monologues/paragraphs.
        :param text: the message content. Fill this arg with all the content you want to send. (required)
        """
        if not self.listening:
            threading.Thread(target=self.run_server, daemon=True).start()
        await super().execute(text)
        self.vla(text)
        self.state.add_to_session("self", text)
        return "Message sent. Return immediately."

    def kill_port(self, port):
        """
        Doesn't seem to help stray listener process
        """
        result = subprocess.run(
            ["lsof", "-t", f"-i:{port}"],
            capture_output=True,
            text=True
        )

        for pid in result.stdout.split():
            os.kill(int(pid), signal.SIGKILL)

    def run_server(self):
        print("Opening socket...")
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", self.chat_port))
            server.listen()
            self.listening = True
        except Exception as e:
            print(f"Failed to start chat server: {e}. Killing and trying again...")
            self.kill_port(self.chat_port)
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

    def restore(self):
        """
        Should address the change in state after sending a context
        """
        if "Current user message" in self.state.impression:
            self.state.add_to_session("User message", self.state.impression["Current user message"])
            self.state.impression = {} # isnt working as intended

    def respond(self, user_input):
        print(f"Message {user_input} received...")
        if self.recorded:
            if self.dataset is None:
                self.dataset = SubDataset("dialogue", "user")
            self.dataset.add_data({"user": [{"content": user_input, "timestamp": timestamp()}]})
        self.state.impression = {"Current user message":f"{user_input}"}
        self.rerun_agent()

    async def start(self, rerun_function: Callable):
        print(f"In Chat start(). Setting rerun_function to {rerun_function}")
        if not self.listening:
            threading.Thread(target=self.run_server, daemon=True).start()
        global runner
        if runner is None:
            runner = rerun_function
        
        if not os.environ.get("INTRODUCTION_DATA", "None") == "None":
            global agent_name
            introduction.introduction_pipeline(rerun=runner, introduction_type=os.environ.get("INTRODUCTION_DATA", "None"), name=agent_name)
        else:
            self.reply("")

    def reply(self, message: str):
        if self.recorded:
            if self.dataset is None:
                self.dataset = SubDataset("dialogue", "user")
            self.dataset.add_data({"robot": [{"content": message, "timestamp": timestamp()}]})
        self.send_q.put(message)

class VLA_Tester(VLA_Complex):
    def __init__(self, interaction_runner, tool_name):
        print("Initializing VLA_Tester")
        self.interaction_runner = interaction_runner
        super().__init__(None, tool_name)
        self.running = False

        # instantiates signal to coordinate monitors with runner (both are in the runner)
        self.signal:dict={"RUNNING_LOOP":True, "RUNNING_E": True, "task":"Stack the blocks"}
        # signal at first blocks episode loop, waiting for "go" from teleop
        self.state = vla_complex_state.State(session=[])

    async def execute(self, instruction: str):
        """
        does a thing
        :param instruction: task to do
        """
        await super().execute(instruction)
        if not self.running:
            threading.Thread(target=self.interaction_runner.run, args=(self.signal,), daemon=True).start()
        if instruction == "STOP":
            self.signal["RUNNING_E"] = False
        else:
            self.signal["RUNNING_LOOP"] = True
            self.signal["RUNNING_E"] = True
            self.signal["task"] = instruction
        print("Action applied. Return immediately.")


class EpisodicRecorder(VLA_Complex):
    """
j
    """
    def __init__(self, interaction_runner, tool_name):
        self.interaction_runner = interaction_runner
        super().__init__(None, tool_name,True)
        self.running = False
        self.conducting = False
        # instantiates signal to coordinate monitors with runner (both are in the runner)
        self.signal:dict={"RUNNING_LOOP":False, "RUNNING_E": True, "task":"Put the cube in the first aid kit"}
        if interaction_runner.demoed:
            self.signal["DECISION"] = None
        # signal at first blocks episode loop, waiting for "go" from teleop
        self.state = vla_complex_state.State(session=[])

    async def execute(self, instruction: str):
        """
        does a thing
        :param instruction: task to do
        """
        await super().execute(instruction)
        self.signal["task"] = instruction
        self.signal["RUNNING_LOOP"] = True
        print(f"Changed signal to {self.signal}")
        if not self.running:
            threading.Thread(target=self.interaction_runner.run, args=(self.signal,), daemon=True).start()
            self.running = True
        print("Success. Return immediately.")

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

        super().__init__(self.drive, tool_name)
        self.drive_updates_on = False
        self.driving = False

        ### State ###
        self.state = vla_complex_state.State(session=[], impression={"current position": "Unknown"})
        self.long_term_memory = []

        self.locations_to_tagIds = dict()
        self.descriptions = {
            "cafe": "there is a red block here",
            "desks": "not much here",
            "lab": "a Spot robot dog",
            "home": "a person"
        }
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
                self.state.impression["current destination"] = location
                self.state.impression["current position"] = f"On route to {location}"
                self.update_description_of_local_position()
                self.base.drive_to_tag(self.default_map, self.locations_to_tagIds[location])
            except Exception:
                return (f"Failed to drive to the location. Make sure {location} is one from {list(self.locations_to_tagIds.keys())}, or \"Dock\" or \"STOP\"")
    
    # helper
    def update_description_of_local_position(self):
        try:
            if self.state.impression["current position"] in self.descriptions:
                self.state.impression[f"known objects at {self.state.impression['current position']}"] = self.descriptions[self.state.impression["current position"]]
            else:
                keys_to_del = []
                for k, v in self.state.impression:
                    if "known objects" in k: # lazy
                        keys_to_del.append(k)
                for k in keys_to_del:
                    del self.state.impression[k]
        except Exception as e:
            print(f"Could not update description of local position: {e}")

    # often has ongoing threads
    def run_drive_updates_client(self):
        self.drive_updates_on = True
        while True:
            while self.driving:
                drive_updates = self.base.drive_updates()["data"]["status"] # good for now
                if "COMPLETE" in drive_updates.values():
                    self.state.impression["current position"] = self.state.impression["current destination"]
                    self.state.impression["current destination"] = None
                    self.update_description_of_local_position()
                    self.driving = False
                    self.rerun("Destination reached.")
                    
            time.sleep(1)

    # is called by an agent, with args. (This call must be non-blocking)
    async def execute(self, location: str):
        """
        Drive to a location. This will actually move the Ava robot in physical space.
        :param location: the exact name of the location from the list of locations (required)
        """
        print("Ava Drive called.")
        await super().execute(location)
        if not self.drive_updates_on:
            threading.Thread(target=self.run_drive_updates_client).start()
        self.driving = True
        self.vla(location)
        
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
        try:
            tags_data = self.base.list_tags(self.default_map)["data"]
        except Exception as e:
            print(f"Could not fetch tags: {e}")
            raise Exception(f"Probably a map error: {e}")
        self.base.pp(tags_data)
        tags_info = tags_data["tags"]

        for id, tag_info in tags_info.items():
            if "tracs" in tag_info["attributes"]:
                self.locations_to_tagIds[tag_info["name"]] = tag_info["id"]
        self.state.impression["locations"] = list(self.locations_to_tagIds.keys())
                
"""
Conclusion:
    Out --> drive_to_tag, list_tags()
                              V
    In  <-- drive_updates, list_tags

"""

class UnityArm(VLA_Complex):
    def __init__(self, tool_name):
        super().__init__(self.act, tool_name)
        self.listening = False
        self.unity_messages = queue.Queue()
        self.out_messages = queue.Queue()
        self.stop_event = threading.Event()
        ### State ###
        self.state = vla_complex_state.State(session=[], impression={
            "carrying": None,
            "available objects": None,
            "available switches": None
        })

        self.cycling = False

    def __str__(self):
        return self.tool_name

    async def execute(self, interact_type: str, object_name: str):
        """
        Use your arm by either passing PICKUP <name of object>, DROP <null>, or SWITCH <name of lever>
        :param interact_type: PICKUP | DROP | SWITCH
        :param object_name: name of object, e.g. Lever 2
        """
        await super().execute(interact_type)
        if not self.listening:
            self.start_listener()
        
        if interact_type == "PICKUP":
            self.vla("PickUp", object_name)
            self.act("GetAvailableObjects", "null")
            return f"Picking up {object_name}. Return immediately."
        elif interact_type == "DROP":
            self.vla("Drop", None)
            self.act("GetAvailableObjects", "null")
            return f"Dropping... Return immediately."
        elif interact_type == "SWITCH":
            self.vla("Switch", object_name)
            self.act("GetAvailableObjects", "null")
            return f"Dropping... Return immediately."
        else:
            return f"Please pass 'PICKUP', 'DROP', 'SWITCH', not {interact_type}"

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
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(("127.0.0.1", 5007))
                break
            except ConnectionRefusedError:
                print("Arm waiting...", end="\r")
                time.sleep(1)
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
        alternate_context = os.environ.get("CONTEXT_TYPE", "A")

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
                self.state.impression["available objects"] = content
                if self.state.impression["carrying"]:
                    #self.update_docstring(self.capability_desc + json.dumps({"Objects you can pick up after a DROP": self.state.impression["available objects"]}))
                    pass
                else:
                    #self.update_docstring(self.capability_desc + json.dumps({"Available objects to pick up": self.state.impression["available objects"]}))
                    pass
            case "available_electric_objects":
                self.state.impression["available switches"] = content
                #self.update_docstring(self.capability_desc + json.dumps({"Things you SWITCH": self.state.impression["available switches"]}))
                pass
            case "status":
                unity_status = content[0]
                print(f"Status returned {unity_status}")
                if "drop" in unity_status:
                    if self.state.impression["carrying"]:
                        self.state.impression["carrying"] = False
                    self.state.add_to_session("Status", unity_status)
                if "switch" in unity_status:
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
        self.act("GetAvailableObjects", "null")
        print("Sent GetAvailableObjects")

        
class UnityDrive(VLA_Complex):
    def __init__(self, tool_name: str):
        super().__init__(self.act, tool_name)
        self.listening = False
        self.unity_messages = queue.Queue()
        self.out_messages = queue.Queue()
        ### State ###
        self.state = vla_complex_state.State(session=[], impression={
            "currently travelling": False,
            "current position": "Initial position",
            "possible destinations": []
        })

        self.unity_functions = None

    def __str__(self):
        return self.tool_name

    async def execute(self, destination: str):
        """
        Provide the destination you'd like to drive to in the Unity environment. The destination must match one of the possible destinations.
        :param destination: one of the possible destinations, by exact name
        """
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
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(("127.0.0.1", 5006))
                break
            except ConnectionRefusedError:
                print("Arm waiting...", end="\r")
                time.sleep(1)
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
            self.act("Closing", "null")
            time.sleep(0.1) # So threads can do a loop
            stop_event.set()
            sock.close()
            print("UnityDrive Socket closed.")

    def react_loop(self, stop_event):
        while not stop_event.is_set():
            msg = self.unity_messages.get()
            self.react(f"{msg}")   

    def react(self, unity_message):
        alternate_context = os.environ.get("CONTEXT_TYPE", "HIGHREFLEXIVITY")
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
            case "meta":
                if content == "quit":
                    print("Quit message received!!")
                    self.listening = False
                    self.agent_sleep()      ############# QUIT CONDITION
                return
            case "destinations":
                print(f"UPDATED DESTINATIONS {content}")
                self.state.impression["possible destinations"] = content
                #self.update_docstring(self.capability_desc + json.dumps({"Function": "SetGoalTo", "Possible args": self.state.impression["possible destinations"]}))
            case "functions":
                self.unity_functions = content
                return
            case "status":
                unity_status = content[0]
                if "reached" in unity_status:
                    self.state.add_to_session("Status", unity_status)
                    self.state.impression["current position"] = unity_status.strip("reached ")
                    self.state.impression["currently travelling"] = False
                    if alternate_context == "LOWREFLEXIVITY": # Kinda hard-coded
                        print("LOWREFLEXIVITY: reflection!")
                        self.rerun_agent()
                    else:
                        print("HIGHREFLEXIVITY")
                elif "goal set" in unity_status:
                    self.state.add_to_session("Status", unity_status)
                    self.state.impression["currently travelling"] = True
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
        self.act("GetFunctions", "null")
        self.act("GetDestinations", "null")

# =========================== Tests =========================== #    
