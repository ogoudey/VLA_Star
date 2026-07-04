from typing import List
from ..vla_star_configurable import VLA_Star_Configurable
from ..context_engine_config.context_engine_configs.chatter_config import ChatterConfig
from ..levels.actuality_levels import Actuality
from ..morphology.morphology import Morphology
from ..morphology.utilities import combine

from ..vla_complex_template.vla_complex_template import VLA_Complex_Template

from vla_star.vla_star import VLA_Star

class ChatterConfigurable(VLA_Star_Configurable):
    def __init__(self,
        config: ChatterConfig,
        actuality: Actuality,
        morphology: Morphology,
        vla_complex_templates: List[VLA_Complex_Template],
        name_kind: str,
    ):
        super().__init__(
            config,
            actuality,
            morphology,
            vla_complex_templates,
            name_kind
        )

    def instantiate(self, **kwargs) -> VLA_Star:
        context_engine = self.instantiate_with_filtered_args(self.config.instantiate, kwargs)

        vla_complexes = []
        for vla_complex_template in self.vla_complex_templates:
            vla_complexes.append(vla_complex_template.instantiate(**kwargs))
        
        name = kwargs["name"] if "name" in kwargs else "unnnamed"

        return VLA_Star(context_engine, vla_complexes, name)