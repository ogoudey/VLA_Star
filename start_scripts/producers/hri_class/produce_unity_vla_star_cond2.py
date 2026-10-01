from starter.starter import Starter

from vla_star.library.instructions import *
from vla_star.library.constructions import *
from vla_star.library.motives import *

from host.manifest_manager import update_manifest
from host.vlanet_interface import update_host_on_vlanet

import sys
from vla_star.vla_complex.vla_complexes.animate import Animate
from vla_star.vla_complex.vla_complexes.unity_drive import Drive
from vla_star.vla_complex.vla_complexes.suspend import Suspend
from vla_star.vla_complex.vla_complexes.game_vla_complexes import EndGame
from vla_star.tool_choice_models.tool import Tool


from vla_star.vla_star import VLA_Star

# This line varies
from vla_star.context_engine.context_engine import OrderedContextLLMEngine

from vla_star.utilities.extension import Extension, Text, Unity
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

    # This line varies
    from vla_star.context_engine.context_engine import OrderedContextLLMEngine

    from vla_star.utilities.extension import VLANet, Text
    vla_star = VLA_Star(
        name,
        OrderedContextLLMEngine(
            context_engine_name=f"test_context_engine",
            construction=ConstructionType.IN_A_UNITY_WORLD.value,
            instructions=InstructionType.ACTUALLY_NAVIGATE_CHECK.value,
            motive=MotiveType.BORN_TO_NAVIGATE.value,
            extra="",
            recorded=True
        ),
        [
            Tool(
                Drive(
                    recorded=False,
                    extension=Unity(address=("127.0.0.1", 5010), project_dir="~/Unity/My\\Project", game_object_name="person1")
                )
            ),
            Tool(
                Chat(
                    recorded=False,
                    extension=Text()
                )
            ),
            Tool(
                Suspend()
            )
        ],
        Extension()
    )

    Host.list_vla_star(vla_star)
    Host.sync_manifest()
    vla_star_starter = Starter(vla_star)
    good = vla_star_starter.start() # no args. But this should be filled.
    vla_star_starter.try_pickle_vla_star()
    Host.update_vla_star_on_list(vla_star)
    Host.sync_manifest()


    
