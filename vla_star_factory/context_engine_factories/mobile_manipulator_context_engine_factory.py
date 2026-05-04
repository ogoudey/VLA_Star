import os
import importlib.util
import sys
from pathlib import Path
from typing import Any, List, Optional
import vla_star.vla_star as vla_star
import vla_star.context_engine as context_engine
import vla_complex.vla_complex as vla_complex
from vla_complex.vlm import VLM
from vla_star.vla_star import VLA_Star
from vla_complex.vla_complex import VLA_Complex

from vla_star.context_engine import OrderedContextLLMEngine, OrderedContextEngineDemoed
import vla_complex.vla_complex as vla_complex

from .context_engine_factory_utilities.instructions import *
from .context_engine_factory_utilities.goals import *

from vla_star_configurable.vla_star_config.vla_star_types import *
from vla_star_configurable.vla_star_config.vla_star_config import VLA_Star_Config

def instantiate_mobile_manipulator_context_engine(
    name: str,
    agency_type: AgencyType | str,
    instructions: InstructionType | str,
    construction: ConstructionType | str,
    motive: MotiveType | str,
    recorded: bool,
    extra: Optional[str] = None
) -> OrderedContextLLMEngine:
    context_engine = None
    match agency_type:
        case AgencyType.AUTO:
            match instructions:
                case InstructionType.TO_PHILOSOPHIZE:
                    _instructions = GOAL3
                case InstructionType.TO_HELP_USER:
                    _instructions = HELP
                case InstructionType.TO_SABOTAGE:
                    _instructions = HARD
                case InstructionType.GOLD:
                    _instructions = GOLD
                case _:
                    _instructions = instructions
            match construction:
                case ConstructionType.TO_PHILOSOPHIZE:
                    _construction = GOAL3
                case ConstructionType.TO_HELP_USER:
                    _construction = HELP
                case ConstructionType.TO_SABOTAGE:
                    _construction = HARD
                case ConstructionType.GOLD:
                    _construction = GOLD
                case _:
                    _construction = construction
            match motive:
                case MotiveType.TO_PHILOSOPHIZE:
                    _motive = GOAL3
                case MotiveType.TO_HELP_USER:
                    _motive = HELP
                case MotiveType.TO_SABOTAGE:
                    _motive = HARD
                case MotiveType.GOLD:
                    _motive = GOLD
                case _:
                    _motive = motive 
            match extra:
                case _:
                    _extra = extra                
            context_engine = OrderedContextLLMEngine(f"context_engine_for_{name}", instructions, construction, _motive, _extra)
        case AgencyType.DEMOED:
            context_engine = OrderedContextEngineDemoed(f"context_engine_for_{name}")
        case _:
            raise ValueError(f"Couldn't instantiate {agency_type}")
            
    if recorded:
        context_engine.recording = True
    return context_engine