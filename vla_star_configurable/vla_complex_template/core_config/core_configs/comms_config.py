from ..core_config import CoreConfig
from ..vla_complex_types import *
from typing import Optional
class CommsConfig(CoreConfig):
    chat_port: int
    def __init__(self,
        chat_port: int,
    ):
        super().__init__()
        self.chat_port = chat_port

    
    def build(self,
        chat_port: Optional[int] = None,
    ):
        from vla_star_factory.core_factories.bidirectional_socket_factory import build_bidirectional_socket
        chat_port = self.chat_port if not chat_port else chat_port

        
        return build_bidirectional_socket(chat_port)
        