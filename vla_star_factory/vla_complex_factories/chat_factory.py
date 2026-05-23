

from vla_complex.vla_complex import VLA_Complex
from vla_complex.vla_complexes.chat import Chat

def instantiate_chat_vla_complex(
        name_tool: str,
        chat_port: int,
        recorded: bool
) -> VLA_Complex:
    return Chat(
        name_tool,
        chat_port,
        recorded=recorded
    )