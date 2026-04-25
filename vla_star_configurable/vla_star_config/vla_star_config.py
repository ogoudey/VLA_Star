from vla_star_configurable.vla_star_config.vla_star_types import *
from typing import Optional

class VLA_Star_Config:
    agency_type: AgencyType
    instructions_type: InstructionType
    construction_type: ConstructionType
    motive_type: MotiveType

    def __init__(self,
        agency_type: AgencyType,
        instruction_type: InstructionType,
        construction_type: ConstructionType,
        motive_type: MotiveType     
    ):
        self.agency_type = agency_type
        self.instructions_type = instruction_type
        self.construction_type = construction_type
        self.motive_type = motive_type