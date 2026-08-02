import threading
from typing import Optional
from ..vla_complex import VLA_Complex
from ..vla_complex_state import State
from ..general_dataset import SubDataset
from vla_star.utilities.displays import timestamp
from vla_star.utilities.extension import Text, VLANet, Internet

from vla_star.utilities.extension import Extension, Unity
class Animate(VLA_Complex):
    recorded: bool
    dataset: Optional[SubDataset] = None
    
    def __init__(self, recorded=False, extension: Extension = Extension()):
        super().__init__("animate", False)
        print(f"[Animate] Initializing.")

        self.recorded = recorded

        ### State ###
        self.state = State(session=[], impression={})

        self.extension = extension

        self.interface = None
        if self.dataset is None and recorded:
            self.dataset = SubDataset("Chat", "user")

        if type(self.extension) is Unity:
            from vla_star.vla_complex.utilities.unity_core import UnityInterface
            self.interface = UnityInterface()
        else:
            raise Exception(f"Extension is not Unity, so not supported.")

    def _repr__(self):
        return f"Chat repr"

    def __str__(self):
        return f"{self.tool_name}"

    async def execute(self, action: str):
        """
        Animate your body by passing one of the actions: \"wave\", \"nod\".
        :param action: the action you want to do. (required)
        """
        print(f"[Animate] Doing \"{action}\"")
        if type(self.extension) is Unity:
            self.interface.act(action)
        else:
            raise Exception(f"Extension is not Unity, so not supported.")