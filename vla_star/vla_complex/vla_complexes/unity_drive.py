import threading
import time
from typing import Optional, List, Dict
from ..vla_complex import VLA_Complex
from ..vla_complex_state import State
from ..general_dataset import SubDataset
from vla_star.utilities.displays import timestamp
from vla_star.utilities.extension import Text, VLANet, Internet

from vla_star.utilities.extension import Extension, Unity

class Drive(VLA_Complex):
    recorded: bool
    dataset: Optional[SubDataset] = None
    
    def __init__(self, recorded=False, extension: Extension = Extension()):
        super().__init__("drive", False)
        print(f"[Drive] Initializing.")

        self.recorded = recorded

        ### State ###
        self.state = State(session=[], impression={})

        self.extension = extension

        self.interface = None
        if self.dataset is None and recorded:
            self.dataset = SubDataset("Drive", "user")

        if type(self.extension) is Unity:
            print(f"[Drive] Importing Unity animate extension")
            from vla_star.vla_complex.utilities.unity_core import UnityInterface
            print(f"[Drive] Create UnityInterface")
            self.interface = UnityInterface(self.extension.host, self.extension.port)
            self.extension.on = True
            threading.Thread(target=self.background_poll_entities, daemon=True).start()
        else:
            raise Exception(f"Extension is not Unity, so not supported.")

    def background_poll_entities(self):
        while self.extension.on:
            try:
                entities_response: List[Dict] = self.interface.get_entities()
                self.state.impression["locations"] = entities_response
            except Exception as e:
                print(f"[Drive] get_entities failed: {e}")
            time.sleep(1)
        

    def _repr__(self):
        return f"Chat repr"

    def __str__(self):
        return f"{self.tool_name}"

    async def execute(self, x: float, y: float, z: float):
        """
        Drive your body to the target position.

        :param x: Target X coordinate.
        :param y: Target Y coordinate.
        :param z: Target Z coordinate.
        """
        destination = (x, y, z)
        print(f"[Drive] Driving to [{destination}]")
        if type(self.extension) is Unity:
            self.interface.navigate_to(entity_id=self.tool_name, destination=destination)
        else:
            raise Exception(f"Extension is not Unity, so not supported.")