from ..vla_star_config import VLA_Star_Config
from ..vla_star_types import *
from .vla_star_utilities import generate_unique_name
from typing import Optional

class MobileManipulatorConfig(VLA_Star_Config):
    def __init__(self,
        agency_type: AgencyType,
        instructions_type: InstructionType,
        construction_type: ConstructionType,
        motive_type: MotiveType
    ):
        super().__init__(
            agency_type=agency_type,
            instruction_type=instructions_type,
            construction_type=construction_type,
            motive_type=motive_type
        )
    
    def instantiate(self,
        name: Optional[str] = None,
        agency_type: Optional[bool] = None,
        instructions: Optional[str] = None,
        construction: Optional[str] = None,
        motive: Optional[str] = None,
        extra: Optional[str] = None,
        recorded: bool = False,
        force_uniqueness: bool=False
    ):
        from vla_star_factory.context_engine_factories.mobile_manipulator_context_engine_factory import instantiate_mobile_manipulator_context_engine
        _name: str = name if name or force_uniqueness else generate_unique_name()
        
        _agency_type = agency_type if agency_type else self.agency_type # should look these up
        _instructions = instructions if instructions else self.instructions_type
        _construction = construction if construction else self.construction_type
        _motive = motive if motive else self.motive_type
        
        instantiate_mobile_manipulator_context_engine(
            name=_name,
            agency_type=_agency_type,
            instructions=_instructions,
            construction=_construction,
            motive=_motive,
            extra=extra,
            recorded=recorded,
        )
        
