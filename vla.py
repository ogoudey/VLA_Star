import threading
from typing import Any

from logger import log

class VLA:
    """Takes a function that takes a string. Can be called like VLA()(...)"""
    def __init__(self):
        pass

    # abstract abc method
    def __call__(self, direction: Any) -> None:
        raise NotImplementedError
    





### Below are currently invalid VLA subclasses

from transmitters import ThroughMessage, one_off

class SimpleDrive(VLA):
    def __init__(self):
        super().__init__()
        self.shared = {"target_message": "stop"}
        through_thread = ThroughMessage(self.shared)
        through_thread.start()
        
        
    def __call__(self, direction: str):
        self.shared["target_message"] = direction

from signals import RecordDatasetSignal

class DatasetRecorderCaller(VLA):
    def __init__(self, dataset_recorder):
        super().__init__()
        self.running_state = {"RUNNING_LOOP": True, "RUNNING_E": True, "task": ""}
        self.dataset_recorder = dataset_recorder
        self.thread = None

    def __call__(self, signal: RecordDatasetSignal):
        print(f"Interpreting signal {signal}")
        if not signal.TASK == "":
            self.running_state["task"] = signal.TASK
        else:
            print(f"No task in signal. Must be the end.")

        self.running_state["RUNNING_E"] = signal.RUNNING_E

        self.running_state["RUNNING_LOOP"] = signal.RUNNING_LOOP
        if self.running_state["RUNNING_LOOP"] == False:
            # do nothing
            if not signal.DATASET_NAME == "":
                self.running_state["dataset_name"] = signal.DATASET_NAME
                print(f"Joining caller's runner thread.")
                self.thread.join()
        elif self.running_state["RUNNING_LOOP"] and not self.thread:
            print(f"Creating new thread for dataset recording...")
            self.thread = threading.Thread(target=self.dataset_recorder.run, args=[self.running_state])
            print("Thread created")
            self.thread.start()

from signals import VLASignal

class SmolVLACaller(VLA):
    def __init__(self, smolvla_runner):
        super().__init__()
        self.running_state = {"instruction": "", "flag": "GO"}
        self.smolvla_runner = smolvla_runner
        self.thread = None   

    def __call__(self, signal: VLASignal):
        print("Using tool SmolVLACaller")
        self.running_state["flag"] = signal.FLAG
        if not signal.INSTRUCTION == self.running_state["instruction"]:
            self.running_state["instruction"] = signal.INSTRUCTION
            if self.thread:
                print("Trying to join...")
                if self.running_state["flag"] == "STOP":
                    self.thread.join()
                    return
            else:
                self.thread = threading.Thread(target=self.smolvla_runner, daemon=True, args=[self.running_state])
                print("Thread created")
                self.thread.start()
            
            print("Back!")
        else:
            print(f"Instruction is the same ({self.running_state['instruction']}")

from pathlib import Path
import sys
import os
path_planning_path = os.environ.get("PATH_PLANNING", "/home/olin/Robotics/AI Planning/Path-Planning")
sys.path.append(path_planning_path)
if not Path(path_planning_path).exists():
    print("No Path Planning")
else:
    import space
    import math
    import terrain_fetcher

import time
class PathFollow(VLA):
    def __init__(self):
        super().__init__()
        self.path: space.Path = None
        self.waypoint: space.SearchNode = None
        self.current_position = None
        self.running_state = {"goal":"", "flag":"GO"}

        self.travel_time = 0

        self.init_env()
        
        
        self.unity_environment = self.init_env()

        self.plan_thread = threading.Thread(target=self.plan)
        self.planning = True
        self.follow_thread = threading.Thread(target=self.follower, daemon=True) 
        self.following = True

    def init_env(self):
        terrain = terrain_fetcher.get_terrain()
        time.sleep(0.1) #needed?
        destinations_json_easy_format = terrain_fetcher.get_destinations()
        self.destinations = []
        destinations_by_name = {}
        for dest in list(destinations_json_easy_format['destinations']):
            self.destinations.append(dest["name"])
            destinations_by_name[dest["name"]] = {"position": dest["position"]}
        try:
            unity_environment = space.UnityEnvironment(terrain_fetcher.get_boat(), destinations_by_name, terrain)
        except ConnectionRefusedError as e:
            print(f"Unity not running...{e}")
            raise Exception(f"Unity not running...")
        except RuntimeError as e:
            print(f"Check sockets... {e}")
            raise Exception(e)
        self.running_state["flag"] = "GO"
        return unity_environment
    


    def __call__(self, signal: dict) -> None:
        #print(f"PathFollow called on {signal}")
        if signal["flag"] == "STOP":
            log(f"Stopping immediately.", self)
            self.running_state["flag"] = signal["flag"]
            signal["flag"] = "DONE"
        else:
            #not signal["goal"] == self.running_state["goal"]:

            self.running_state["goal"] = signal["goal"]
            if self.plan_thread.is_alive():
                self.planning = True
            else:
                self.plan_thread.start()
        signal["flag"] = "CONTINUE"
            
    def plan(self):
        while True:
            if self.planning:
                log(f"Pathing to {self.running_state["goal"]}", self)

                try:
                    self.unity_environment = self.init_env()
                    self.path = space.rrt_astar(self.unity_environment, self.running_state["goal"], num_nodes=5000, terrain_aabb=((0, 1000), (0, 1000)), costly_altitude=0.01, logger=log)
                except Exception as e:
                    log(f"Planning failed because {e}", self)
                if self.running_state["flag"] == "STOP":
                    self.planning = False
                    continue # don't start the follower if we want to replan
                if self.follow_thread.is_alive():
                    self.following = True
                else:
                    self.follow_thread.start()
                self.planning = False
            time.sleep(1)


    def next_waypoint(self):
        #print(f"New from {self.path.nodes}")
        if not len(self.path.nodes) > 0:
            print("Thread dieing because no path to follow")
            raise Exception(f"No path to follow...")
        self.waypoint = self.path.nodes.pop(0)
    
    def follower(self):
        log(f"Follower thread started with {self.running_state}", self)
        try:
            while True:
                if self.following:
                    travel_t0 = time.time()
                    while not self.running_state["flag"] == "STOP":
                        if not self.waypoint:
                            self.next_waypoint()
                        
                        if self.current_position:
                            self.travel_time = time.time() - travel_t0
                            d = math.sqrt( math.pow(self.waypoint.state.coordinates[0] - self.current_position[0], 2) + math.pow(self.waypoint.state.coordinates[1] - self.current_position[1], 2) )
                            #print(f"{self.current_position} is {d} away from {self.waypoint.state.coordinates}")
                            if d < 1:
                                log(f"Arrived at waypoint {self.waypoint.state.coordinates}", self)
                                if len(self.path.nodes) > 0:
                                    log(f"Path is not empty, updating waypoint.", self)
                                    self.next_waypoint()
                                else:
                                    log(f"Path is empty, sending STOP", self)
                                    self.running_state["flag"] = "STOP"
                                    one_off("STOP")
                                    
                        if self.running_state["flag"] == "STOP":
                            continue
                        self.follow()
                    self.following = False
                log(f"Stopping because {self.running_state}", self)
                one_off("STOP")
                time.sleep(1)

        except Exception as e:
            print(f"!!{e}!!")

    def follow(self):
        self.current_position = one_off(self.waypoint.as_message())
        return self.current_position



