from ..vla_complex_config import VLA_Complex_Config
from ..vla_complex_types import *
from typing import Optional


class SO101ManipulationDemoConfig(VLA_Complex_Config):
    dataset_name: str

    def __init__(self,
        dataset_name: str,
        recorded: bool
    ):
        self.dataset_name = dataset_name
        super().__init__(
            AgencyType.DEMOED,
            monitor_types=[],
            recorded=recorded
        )