from vla_star_configurable.context_engine_config.vla_star_types import *
from vla_star_factory.context_engine_factories.library.instructions import *
from vla_star_factory.context_engine_factories.library.constructions import *
from vla_star_factory.context_engine_factories.library.motives import *
from typing import Optional

class ContextEngineConfig:
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