from starter.starter import Starter

from vla_star.library.instructions import *
from vla_star.library.constructions import *
from vla_star.library.motives import *

from host.manifest_manager import update_manifest
from host.vlanet_interface import update_host_on_vlanet

import sys

from vla_star.vla_complex.vla_complexes.chat import Chat
from vla_star.vla_complex.vla_complexes.suspend import Suspend
from vla_star.vla_complex.vla_complexes.game_vla_complexes import StartGame
from vla_star.tool_choice_models.tool import Tool
from host.host import Host

if __name__ == "__main__":
    name = sys.argv[1]

    vla_star_starter = Starter.try_load_by_name(sys.argv[1])
    if vla_star_starter:
        print(f"Already found")
        sys.exit(1)

    from vla_star.vla_star import VLA_Star

    from vla_star.context_engine.context_engine import OrderedContextLLMEngine

    from vla_star.utilities.extension import VLANet, Text
    vla_star = VLA_Star(
        name,
        OrderedContextLLMEngine(
            context_engine_name=f"context_engine_for_{name}",
            construction=ConstructionType.GAME_BOUNCER.value,
            instructions=InstructionType.GAME_BOUNCER.value,
            motive=MotiveType.GAME_BOUNCER.value,
            extra="",
            recorded=True
        ),
        [
            Tool(
                Chat(
                    recorded=False,
                )
            ),
            Tool(
                Suspend()
            ),
            Tool(
                StartGame()
            )
        ],
        VLANet()
    )

    vla_star_starter = Starter(vla_star)
    good = vla_star_starter.start() # no args. But this should be filled.
    vla_star_starter.try_pickle_vla_star()  
