import threading
from typing import Any

class VLA:
    """Takes a function that takes a string. Can be called like VLA()(...)"""
    def __init__(self):
        pass

    def __call__(self, direction: Any):
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

class SmolVLACaller(VLA):
    def __init__(self, smolvla_runner):
        super().__init__()
        self.running_signal = {"instruction": "", "flag": "GO"}
        self.smolvla_runner = smolvla_runner
        self.thread = None   

    def __call__(self, signal: dict[str, str]):
        print("Using tool SmolVLACaller")
        self.running_signal["flag"] = signal["flag"]
        if not signal["instruction"] == self.running_signal["instruction"]:
            self.running_signal["instruction"] = signal["instruction"]
            if self.thread:
                print("Trying to join...")
                if self.running_signal["flag"] == "STOP":
                    self.thread.join()
                    return
            else:
                self.thread = threading.Thread(target=self.smolvla_runner, daemon=True, args=[self.running_signal])
                print("Thread created")
                self.thread.start()
            
            print("Back!")
        else:
            print(f"Instruction is the same ({self.running_signal['instruction']}")

from pathlib import Path
import sys
sys.path.append("/home/olin/Robotics/AI Planning/Path-Planning")
if not Path("/home/olin/Robotics/AI Planning/Path-Planning").exists():
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
        self.init_env()
        
        self.running_signal = {"goal":"", "flag":"GO"}
        self.unity_environment = self.init_env()

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
        return unity_environment
    
    def __call__(self, instruction: str):
        if instruction == "STOP":
            self.running_signal["flag"] = instruction
        elif not instruction == self.running_signal["goal"]:
            goal = instruction
            print(f"Pathing to {goal}")
            try:
                self.plan(goal)
                self.running_signal["goal"] = goal
            except Exception as e:
                raise Exception(f"Could not make new path: {e}")
            
            if self.thread.is_alive():
                self.thread.join()
            self.thread = threading.Thread(target=self.follower, daemon=True, args=[self.running_signal])
            print("Thread created")
            
            self.thread.start()
        else:
            print(f"No new goal... continuing...")
            pass
        return "CONTINUE"
            
    def plan(self, goal):
        self.path = space.rrt_astar(self.unity_environment, goal)

    def next_waypoint(self):
        print(f"New from {self.path.nodes}")
        if not len(self.path.nodes) > 0:
            print("Thread dieing because no path to follow")
            raise Exception(f"No path to follow...")
        self.waypoint = self.path.nodes.pop(0)
    
    def follower(self, running_signal):
        while not running_signal["flag"] == "STOP":
            if not self.waypoint:
                self.next_waypoint()
            
            if self.current_position:
                d = math.sqrt( math.pow(self.waypoint.state.coordinates[0] - self.current_position[0], 2) + math.pow(self.waypoint.state.coordinates[1] - self.current_position[1], 2) )
                #print(f"{self.current_position} is {d} away from {self.waypoint.state.coordinates}")
                if d < 1:
                    print(f"Arrived at waypoint {self.waypoint.state.coordinates}")
                    if len(self.path.nodes) > 0:
                        print(f"Path is not empty, updating waypoint.")
                        self.next_waypoint()
                    else:
                        print(f"Path is empty, sending STOP")
                        self.running_signal = {"goal":"", "flag":"STOP"}
                        one_off("STOP")
                        
            if not running_signal["flag"] == "STOP":
                self.follow()

    def follow(self):
        self.current_position = one_off(self.waypoint.as_message())
        return self.current_position



