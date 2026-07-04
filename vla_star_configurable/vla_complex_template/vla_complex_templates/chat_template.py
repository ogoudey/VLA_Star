from ..vla_complex_template import VLA_Complex_Template
from ..core_config.core_configs.comms_config import CommsConfig
from vla_complex.vla_complexes.chat import Chat

class ChatTemplate(VLA_Complex_Template):
    def __init__(self,
        comms_config: CommsConfig,
        tool_name: str = "chat_tool",
        description: str ="""\
        Say something directly to user. Use this for informal realistic conversation. Be as realistic as you can, no monologues/paragraphs.
        :param text: the message content. Fill this arg with all the content you want to send. (required)\
        """,
        return_value: str = "Message sent. Return immediately.",
        on_start: bool = True,
        monitors=[],
        recorded: bool = True
    ):
        super().__init__(
            [comms_config],
            tool_name,
            description,
            return_value,
            on_start,
            monitors,
            recorded
        )
    
    def instantiate(self, **kwargs) -> Chat:
        bidirectional_socket = self.build_with_filtered_args(self.configs[0].build, kwargs)
        return Chat(bidirectional_socket, self.tool_name, self.description, self.return_value, self.on_start, self.monitors, self.recorded)
