from ..vla_complex_config import VLA_Complex_Config
from ..vla_complex_types import *
from typing import Optional
class ChatConfig(VLA_Complex_Config):
    def __init__(self,
        recorded: bool,
        chat_port: int,
    ):
        self.chat_port = chat_port
        super().__init__(
            agency_type=AgencyType.AUTO,
            monitor_types=[],
            recorded=recorded
        )
    
    def instantiate(self,
        chat_tool_name: Optional[str] = None,
        chat_port: Optional[int] = None,
        recorded: Optional[bool] = None
    ):
        from vla_star_factory.vla_complex_factories.chat_factory import instantiate_chat_vla_complex
        chat_tool_name = "chat_tool" if not chat_tool_name else chat_tool_name
        chat_port = self.chat_port if not chat_port else chat_port
        recorded = self.recorded if recorded is None else recorded

        
        return instantiate_chat_vla_complex(chat_tool_name, chat_port, recorded)
        