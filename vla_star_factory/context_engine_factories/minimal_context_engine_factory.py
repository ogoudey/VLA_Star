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

from vla_star.context_engine import OrderedContextLLMEngine, OrderedContextEngineDemoed, OrderedContextEngine
import vla_complex.vla_complex as vla_complex

from .library.instructions import *
from .library.constructions import *
from .library.motives import *

from vla_star_configurable.vla_star_config.vla_star_types import *
from vla_star_configurable.vla_star_config.vla_star_config import VLA_Star_Config

def instantiate_minimal_context_engine(
    name: str,
    agency_type: AgencyType | str,
    instructions: InstructionType | str,
    construction: ConstructionType | str,
    motive: MotiveType | str,
    recorded: bool,
    extra: Optional[str] = None
) -> OrderedContextEngine:
    context_engine = None
    match agency_type:
        case AgencyType.AUTO:
            match instructions:
                case InstructionType.MIMINAL:
                    _instructions = MIMINAL_INSTRUCTIONS
                case _:
                    _instructions = instructions
            match construction:
                case ConstructionType.YOURE_STATIONARY:
                    _construction = YOURE_STATIONARY
                case _:
                    _construction = construction
            match motive:
                case MotiveType.MINIMAL:
                    _motive = MINIMAL_MOTIVE
                case _:
                    _motive = motive 
            match extra:
                case _:
                    _extra = extra                
            context_engine = OrderedContextLLMEngine(f"context_engine_for_{name}", _instructions, _construction, _motive, _extra)
        case AgencyType.DEMOED:
            context_engine = OrderedContextEngineDemoed(f"context_engine_for_{name}")
        case _:
            raise ValueError(f"Couldn't instantiate {agency_type}")
            
    if recorded:
        context_engine.recording = True
    return context_engine