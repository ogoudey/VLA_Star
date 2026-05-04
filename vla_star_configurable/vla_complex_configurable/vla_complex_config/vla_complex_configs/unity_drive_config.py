from ..vla_complex_config import VLA_Complex_Config
from ..vla_complex_types import *

class UnityDriveConfig(VLA_Complex_Config):
    def __init__(self):
        super().__init__(
            agency_type=AgencyType.AUTO,
            monitor_types=[],
            recorded=False
        )