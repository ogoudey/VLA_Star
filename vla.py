import threading
from typing import Any

class VLA:
    """Takes a function that takes a string. Can be called like VLA()(...)"""
    def __init__(self):
        pass

    def __call__(self, direction: Any):
        raise NotImplementedError
    

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

from pathlib import Path
import sys
sys.path.append("/home/olin/Robotics/AI Planning/Path-Planning")
if not Path("/home/olin/Robotics/AI Planning/Path-Planning").exists():
    print("No Path Planning")
else:
    import space
    import math
    import terrain_fetcher

class PathFollow(VLA):
    def __init__(self):
        super().__init__()
        self.path: space.Path = None
        self.waypoint: space.SearchNode = None
        self.last_goal: str = ""
        self.current_position = None

        
        try:
            self.unity_environment = space.UnityEnvironment(terrain_fetcher.get_boat(), terrain_fetcher.get_destinations(), terrain_fetcher.get_terrain())
        except ConnectionRefusedError as e:
            print(f"Unity not running...{e}")
            raise Exception(f"Unity not running...")
        except RuntimeError as e:
            print(f"Check sockets... {e}")
            raise Exception(e)

    def __call__(self, goal: str):
        print(f"Pathing to {goal}")
        if not goal == self.last_goal:
            try:
                self.plan(goal)
                self.last_goal = goal
            except Exception as e:
                raise Exception(f"Could not make new path: {e}")
        else:
            if self.current_position:
                d = math.sqrt( math.pow(self.waypoint.state.coordinates[0] - self.current_position[0], 2) + math.pow(self.waypoint.state.coordinates[1] - self.current_position[1], 2) )
                print(f"{self.current_position} is {d} away from {self.waypoint.state.coordinates}")
                if d < 1:
                    is_next = self.next_waypoint()
                    if not is_next:
                        return "DONE"

            self.follow()
        return "CONTINUE"
            
    def plan(self, goal):
        self.path = space.rrt_astar(self.unity_environment, goal)

    def next_waypoint(self):
        print("NEW WAYPOINT")
        if not len(self.path.nodes) > 0:
            print(f"No path to follow...")
            return False
        self.waypoint = self.path.nodes.pop(0)
        return True

    def follow(self):
        if len(self.path.nodes) == 0:
            return f"No path to follow..."
        if not self.waypoint:
            self.next_waypoint()
        
        self.current_position = one_off(self.waypoint.as_message())
        return self.current_position



