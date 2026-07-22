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


from vla_star.vla_star import VLA_Star

# This line varies
from vla_star.context_engine.context_engine import OrderedContextLLMEngine

from vla_star.utilities.extension import Extension, Text
"""
vla_star = VLA_Star(
    name,
    OrderedContextLLMEngine(
        context_engine_name=f"context_engine_for_{name}",
        construction=ConstructionType.THINKING_OF_A_NUMBER.value,
        instructions=InstructionType.THINKING_OF_A_NUMBER.value,
        motive=MotiveType.THINKING_OF_A_NUMBER.value,
        extra="",
        recorded=True
    ),
    [
        Tool(
            Chat(
                chat_port=5001,
                recorded=False,
            )
        ),
        Tool(
            Suspend()
        ),
        Tool(
            EndGame()
        )
    ],
    Extension()
)
"""
def test_produce_a_context_engine():
    context_engine1 = OrderedContextLLMEngine(
        context_engine_name=f"test_context_engine",
        construction=ConstructionType.THINKING_OF_A_NUMBER.value,
        instructions=InstructionType.THINKING_OF_A_NUMBER.value,
        motive=MotiveType.THINKING_OF_A_NUMBER.value,
        extra="",
        recorded=True
    )

def test_produce_a_vla_complex():
    chat = Chat(
        recorded=False,
    )
    assert type(chat.extension) is Text

def test_produce_a_tool():
    tool = Tool(
        Chat(
            recorded=False,
        )
    )
    print(f"\n\n{tool.tool_dict}")
    assert tool.tool_dict["name"] == "chat"

def test_produce_vla_star():
    vla_star = VLA_Star(
        "test",
        OrderedContextLLMEngine(
            context_engine_name=f"test_context_engine",
            construction=ConstructionType.THINKING_OF_A_NUMBER.value,
            instructions=InstructionType.THINKING_OF_A_NUMBER.value,
            motive=MotiveType.THINKING_OF_A_NUMBER.value,
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
            )
        ],
        Extension()
    )
    assert len(VLA_Star._activated) == 1




