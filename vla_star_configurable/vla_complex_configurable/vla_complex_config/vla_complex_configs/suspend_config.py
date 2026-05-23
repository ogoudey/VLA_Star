from ..vla_complex_config import VLA_Complex_Config
from ..vla_complex_types import *
from typing import Optional

class SuspendConfig(VLA_Complex_Config):
    def __init__(self):
        super().__init__(
            agency_type=AgencyType.AUTO,
            monitor_types=[],
            recorded=False
        )
    
    def instantiate(self,
        suspend_tool_name: Optional[str] = None,
    ):
        from vla_star_factory.vla_complex_factories.suspend_factory import instantiate_suspend_vla_complex
        suspend_tool_name = "suspend_tool" if not suspend_tool_name else suspend_tool_name
        
        return instantiate_suspend_vla_complex(suspend_tool_name)
        