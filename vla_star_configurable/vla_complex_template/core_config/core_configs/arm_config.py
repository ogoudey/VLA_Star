from ..core_config import VLA_Complex_Config
from ..vla_complex_types import *
from typing import Optional

class ArmConfig(VLA_Complex_Config):
    def __init__(self):
        super().__init__(
            agency_type=AgencyType.AUTO,
            monitor_types=[],
            recorded=False
        )
    
    def instantiate(self,
        tool_name: Optional[str] = None,
        teleop_port: Optional[int] = None,
        recorded: Optional[bool] = None
    ):
        from vla_star_factory.core_factories.bidirectional_socket_factory import instantiate_chat_vla_complex
        chat_tool_name = "chat_tool" if not tool_name else tool_name
        teleop_port = self.teleop_port if not teleop_port else teleop_port
        recorded = self.recorded if recorded is None else recorded

        
        return instantiate_chat_vla_complex(chat_tool_name, chat_port, recorded)