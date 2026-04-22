import os
import importlib.util
import sys
from pathlib import Path
from typing import Any, List, Optional
import vla_star
import gda
import vla_complex
import vla
from vlm import VLM
from vla_star import VLA_Star
from vla_complex import VLA_Complex

from vla import VLA
from gda import OrderedContextDemoed, OrderedContextLLMAgent
import vla_complex

from .utilities.instructions import *
from .utilities.goals import *

from vla_star_configurable.vla_star_config.vla_star_types import *
from vla_star_configurable.vla_star_config.vla_star_config import VLA_Star_Config

def build_mobile_manipulator_agent(config: VLA_Star_Config) -> OrderedContextLLMAgent:
    agent = None
    name = os.environ.get("AGENT_LABEL", "def")
    match config.motive_type:
        case MotiveType.TO_PHILOSOPHIZE:
            agent = OrderedContextLLMAgent(name, INSTRUCTIONS25, GOAL3)
        case MotiveType.TO_HELP_USER:
            agent = OrderedContextLLMAgent(name, INSTRUCTIONS2, HELP)
        case MotiveType.TO_SABOTAGE:
            agent = OrderedContextLLMAgent(name, INSTRUCTIONS2, HARD)
        case MotiveType.GOLD:
            agent = OrderedContextLLMAgent(name, INSTRUCTIONS2, GOLD)
        case None:
            agent = OrderedContextLLMAgent(name, INSTRUCTIONS2)
        case _:
            raise ValueError(f"Unsupported motive type: {config.motive_type}")
    if config.recorded:
        agent.recording = True
    return agent