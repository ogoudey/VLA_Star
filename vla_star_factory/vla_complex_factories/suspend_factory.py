

from vla_complex.vla_complex import VLA_Complex
from vla_complex.vla_complexes.suspend import Suspend

def instantiate_suspend_vla_complex(
    name_tool: str,
) -> VLA_Complex:
    return Suspend(
        name_tool,
    )