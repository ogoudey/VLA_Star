from typing import List
from vla_star_configurable.context_engine_config.context_engine_config import ContextEngineConfig
from vla_star_configurable.levels.actuality_levels import Actuality
from vla_star_configurable.morphology.morphology import Morphology

from vla_star_configurable.vla_complex_template.vla_complex_template import VLA_Complex_Template
from vla_star_configurable.configurable import Configurable
from abc import abstractmethod

class VLA_Star_Configurable(Configurable):
    context_engine_config: ContextEngineConfig
    actuality: Actuality
    morphology: Morphology
    vla_complex_templates: List[VLA_Complex_Template]
    name_kind: str
    validated: bool

    def __init__(self,
        config: ContextEngineConfig,
        actuality: Actuality,
        morphology: Morphology,
        vla_complex_templates: List[VLA_Complex_Template],
        name_kind: str,
    ):
        self.config = config
        self.actuality = actuality
        self.morphology = morphology
        self.vla_complex_templates = vla_complex_templates
        self.name_kind = name_kind