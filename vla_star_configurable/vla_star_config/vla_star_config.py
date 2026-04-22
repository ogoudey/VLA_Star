from vla_star_configurable.vla_star_config.vla_star_types import *
from typing import Optional

class VLA_Star_Config:
    agency_type: AgencyType
    recorded: bool
    motive_type: Optional[MotiveType]

    def __init__(self,
        agency_type: AgencyType,
        recorded: bool,
        motive_type: Optional[MotiveType]       
    ):
        self.agency_type = agency_type
        self.recorded = recorded
        self.motive_type = motive_type
