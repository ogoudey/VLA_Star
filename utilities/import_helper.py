import sys
from pathlib import Path
import os

def find(module_name: str):
    match module_name:
        case "vla_interface":
            custom_brains = Path(os.environ.get("LEROBOT", "/home/mulip-guest/LeRobot/lerobot/custom_brains"))#import editable lerobot for VLA
            sys.path.append(custom_brains.as_posix())
            if not custom_brains.exists():
                print("No SmolVLA")
                raise FileNotFoundError(f"Could not add {custom_brains} to sys.path")
            try:
                import vla_interface as module
            except Exception as e:
                print(e)
                raise FileNotFoundError("Failed to import LeRobot etc.")
        case "ava_base":
            py_ava_tools = Path(os.environ.get("AVA_BASE", "/home/olin/Robotics/Projects/Ava/py_ava_tools"))
            sys.path.append(py_ava_tools.as_posix())
            if not py_ava_tools.exists():
                print("No Ava Base!")
                raise FileNotFoundError(f"Could not add {py_ava_tools} to sys.path.\n{sys.path}\n_______________")
            try:
                from ava_base import ava as module
            except Exception as e:
                print(e)
                raise FileNotFoundError("Failed to import ava_base etc.")
        case _:
            raise ValueError(f"{module_name} has not been implemented in the import_helper!")
    return module