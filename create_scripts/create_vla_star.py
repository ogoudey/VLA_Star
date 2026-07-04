from instantiator.instantiator import Instantiator

from vla_star_factory.context_engine_factories.library.instructions import *
from vla_star_factory.context_engine_factories.library.constructions import *
from vla_star_factory.context_engine_factories.library.motives import *

from host.manifest_manager import update_manifest
from host.vlanet_interface import update_host_on_vlanet

import sys

from vla_complex.vla_complexes.chat import Chat
from vla_complex.vla_complexes.suspend import Suspend
from vla_complex.vla_complexes.game_vla_complexes import StartGame
from tool_choice_models.tool import Tool
if __name__ == "__main__":
    name = sys.argv[1]

    vla_star_instantiator = Instantiator.try_load_by_name(sys.argv[1])
    if vla_star_instantiator:
        print(f"Already found")
        sys.exit(1)

    from vla_star.vla_star import VLA_Star

    # This line varies
    from vla_star.context_engine import OrderedContextLLMEngine

    from vla_star.extension import Extension
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
                    chat_port=5001,
                    recorded=False,
                    extension=Extension()
                )
            ),
            Tool(
                Suspend()
            ),
            Tool(
                StartGame()
            )
        ],
        Extension()
    )


    vla_star_instantiator = Instantiator(vla_star)
    good = vla_star_instantiator.instantiate() # no args. But this should be filled.
    vla_star_instantiator.try_pickle_vla_star()
    
