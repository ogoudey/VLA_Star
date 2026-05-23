from vla_star_configurable.vla_complex_configurable.vla_complex_config.vla_complex_config import VLA_Complex_Config
from vla_star.vla_star import VLA_Star
from ..configurable import Configurable

class VLA_Complex_Configurable(Configurable):
    vla_complex_config: VLA_Complex_Config
    name: str

    def __init__(self,
        vla_complex_config: VLA_Complex_Config,
        name: str
    ):
        self.vla_complex_config = vla_complex_config
        self.name = name



    