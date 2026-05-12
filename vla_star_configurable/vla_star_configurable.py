from typing import List
from vla_star_configurable.vla_star_config.vla_star_config import VLA_Star_Config
from vla_star_configurable.levels.actuality_levels import Actuality
from vla_star_configurable.morphology.morphology import Morphology

from vla_star_configurable.vla_complex_configurable.vla_complex_configurable import VLA_Complex_Configurable
import inspect
from vla_star_configurable.configurable import Configurable
from abc import abstractmethod
import pprint

class VLA_Star_Configurable(Configurable):
    config: VLA_Star_Config
    actuality: Actuality
    morphology: Morphology
    vla_complex_configurables: List[VLA_Complex_Configurable]
    name_kind: str

    validated: bool

    def instantiate_with_filtered_args(self, func, kwargs):
        valid = inspect.signature(func).parameters
        kwargs = {k: v for k, v in kwargs.items() if k in valid}
        return func(**kwargs)

    def __init__(self,
        config: VLA_Star_Config,
        actuality: Actuality,
        morphology: Morphology,
        vla_complex_configurables: List[VLA_Complex_Configurable],
        name_kind: str,
    ):
        self.config = config
        self.actuality = actuality
        self.morphology = morphology
        self.vla_complex_configurables = vla_complex_configurables
        self.name_kind = name_kind
    
    
    @abstractmethod
    def instantiate(self, **kwargs):
        raise NotImplementedError()