import threading
import socket
import time
import queue
from typing import Callable
import socket
import os
import json

from ..vla_complex import VLA_Complex
from vla_complex.vla_complex_state import State
from ..utilities import chat_utilities

class UnityDrive(VLA_Complex):
    def __init__(self, tool_name: str):
        super().__init__(self.act, tool_name)
        self.listening = False
        self.unity_messages = queue.Queue()
        self.out_messages = queue.Queue()
        ### State ###
        self.state = State(session=[], impression={
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
        
        stop_event = threading.Event()

        threading.Thread(
            target=chat_utilities.recv_loop,
            args=(sock, self.unity_messages, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=chat_utilities.send_loop,
            args=(sock, self.out_messages, stop_event),
            daemon=True
        ).start()

        threading.Thread(
            target=self.react_loop,
            args=(stop_event,),
            daemon=True
        ).start()

        try:
            while self.listening and not stop_event.is_set():
                time.sleep(1)
        finally:
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
        self.rerun_agent()
        self.act("GetFunctions", "null")
        self.act("GetDestinations", "null")