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

from transmitters import ThroughMessage

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

class PathFollow(VLA):
    def __init__(self):
        super().__init__()
        self.path = []
        print(space.__file__)

    def __call__(self, goal: str):
        print(f"Pathing to {goal}")
        try:
            self.plan(goal)
        except Exception as e:
            raise Exception(e)

    def plan(self, goal):
        import terrain_fetcher
        print("imported")
        heightmap = terrain_fetcher.get_terrain()
        print(heightmap)

        self.path = space.unity()

    def follow(self):
        self.shared = {"target_message": "stop"}
        through_thread = ThroughMessage(self.shared)
        through_thread.start()



