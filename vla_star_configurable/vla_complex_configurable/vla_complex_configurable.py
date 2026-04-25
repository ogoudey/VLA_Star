from vla_complex_configs.vla_complex_config import VLA_Complex_Config

from ..configurable import Configurable

from abc import abstractmethod



class VLA_Complex_Configurable(Configurable):
    vla_complex_config: VLA_Complex_Config
    name: str

    def configure(self):
        pass

    def __init__(self,
        vla_complex_config: VLA_Complex_Config,
        name: str
    ):
        self.vla_complex_config = vla_complex_config
        self.name = name

    @abstractmethod
    def instantiate(self):
        raise NotImplementedError()