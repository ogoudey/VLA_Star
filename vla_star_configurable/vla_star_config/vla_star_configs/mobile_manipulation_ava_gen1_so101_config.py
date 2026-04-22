from ..vla_star_config import VLA_Star_Config
from ..vla_star_types import *

class MobileManipulatorAvaGen1SO101Config(VLA_Star_Config):
    def __init__(self,
        auto: bool,
        recorded: bool
    ):
        agency_type = AgencyType.AUTO if auto else AgencyType.DEMOED
        super().__init__(
            agency_type=agency_type,
            recorded=recorded,
            motive_type=MotiveType.TO_PHILOSOPHIZE
        )
