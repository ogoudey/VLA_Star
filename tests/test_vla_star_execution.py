# PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests

import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent
sys.path.append(str(parent_dir.parent))

from vla_star.library.instructions import *
from vla_star.library.constructions import *
from vla_star.library.motives import *

from host.manifest_manager import update_manifest
from host.vlanet_interface import update_host_on_vlanet



from vla_star.vla_complex.vla_complexes.chat import Chat
from vla_star.vla_complex.vla_complexes.suspend import Suspend
from vla_star.vla_complex.vla_complexes.game_vla_complexes import EndGame
from vla_star.tool_choice_models.tool import Tool
import pytest


from vla_star.vla_star import VLA_Star

# This line varies
from vla_star.context_engine.context_engine import OrderedContextLLMEngine

from vla_star.utilities.extension import Extension, Text
import asyncio

def test_execute_a_vla_complex():
    suspend = Suspend()
    with pytest.raises(KeyboardInterrupt):
        asyncio.run(suspend.execute())