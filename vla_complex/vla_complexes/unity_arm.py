import threading

from ..vla_complex import VLA_Complex
from vla_complex_state import State

import queue
import json

class UnityArm(VLA_Complex):
    def __init__(self, tool_name):
        super().__init__(self.act, tool_name)
        self.listening = False
        self.unity_messages = queue.Queue()
        self.out_messages = queue.Queue()
        self.stop_event = threading.Event()
        ### State ###
        self.state = State(session=[], impression={
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