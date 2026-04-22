from typing import List
from vla_star_configs.vla_star_config import VLA_Star_Config
from levels.actuality_levels import Actuality
from morphologies.morphology import Morphology

from vla_complex_configurables.vla_complex_configurable import VLA_Complex_Configurable

from configurable import Configurable
from abc import abstractmethod

class VLA_Star_Configurable(Configurable):
    config: VLA_Star_Config
    actuality: Actuality
    morphology: Morphology
    vla_complex_configurables: List[VLA_Complex_Configurable]
    name: str

    validated: bool

    def configure(self):
        pass

    def __init__(self,
        config: VLA_Star_Config,
        actuality: Actuality,
        morphology: Morphology,
        vla_complex_configurables: List[VLA_Complex_Configurable],
        name: str,
    ):
        self.config = config
        self.actuality = actuality
        self.morphology = morphology
        self.vla_complex_configurables = vla_complex_configurables
        self.name = name
    
    
    @abstractmethod
    def build(self):
        raise NotImplementedError()