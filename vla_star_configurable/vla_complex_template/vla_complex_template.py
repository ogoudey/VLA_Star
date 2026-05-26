from vla_star_configurable.vla_complex_template.core_config.core_config import CoreConfig
from vla_star.vla_star import VLA_Star
from ..configurable import Configurable
from typing import List
class VLA_Complex_Template(Configurable):
    configs: List[CoreConfig]
    tool_name: str
    description: str
    return_value: str
    on_start: bool
    monitors: List

    def __init__(self,
        configs: List[CoreConfig],
        tool_name: str,
        description: str,
        return_value: str,
        on_start: bool,
        monitors: List,
        recorded: bool
    ):
        self.configs = configs
        self.tool_name = tool_name
        self.description = description
        self.return_value = return_value
        self.on_start = on_start
        self.monitors = monitors
        self.recorded = recorded


    