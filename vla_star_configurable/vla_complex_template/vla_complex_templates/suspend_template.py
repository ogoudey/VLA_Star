from ..vla_complex_template import VLA_Complex_Template
from ..core_config.core_configs.suspend_config import SuspendConfig
from vla_complex.vla_complexes.suspend import Suspend
class SuspendTemplate(VLA_Complex_Template):
    def __init__(self,
        suspend_config: SuspendConfig,
        tool_name: str = "suspend_tool",
        description: str ="""\
        Deactivate yourself. This suspends all of your future capabilities until you are woken up ("activated") again.\
        """,
        return_value: str = "Message sent. Return immediately.",
        on_start: bool = True,
        monitors=[],
        recorded: bool = True
    ):
        super().__init__(
            [suspend_config],
            tool_name,
            description,
            return_value,
            on_start,
            monitors,
            recorded
        )
    
    def instantiate(self, **kwargs) -> Suspend:
        # would build config here, but the config is empty
        return Suspend(self.tool_name, self.description, self.return_value, self.on_start, self.monitors, self.recorded)
