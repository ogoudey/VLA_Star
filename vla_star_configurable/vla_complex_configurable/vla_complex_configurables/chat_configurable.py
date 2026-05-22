from ..vla_complex_configurable import VLA_Complex_Configurable
from ..vla_complex_config.vla_complex_configs.chat_config import ChatConfig

class ChatConfigurable(VLA_Complex_Configurable):
    def __init__(self,
        vla_complex_config: ChatConfig,
        name: str
    ):
        super().__init__(
            vla_complex_config,
            name
        )
    
    def instantiate(self):
        from vla_complex.vla_complexes.chat import Chat
        return Chat("chat")
