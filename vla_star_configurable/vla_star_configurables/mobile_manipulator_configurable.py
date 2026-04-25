from typing import List
from ..vla_star_configurable import VLA_Star_Configurable
from ..vla_star_config.vla_star_configs.mobile_manipulator_config import MobileManipulatorConfig
from ..levels.actuality_levels import Actuality

from ..morphology.morphologies.ava_gen1 import AvaGen1
from ..morphology.morphologies.so101 import SO101
from ..morphology.morphology import Morphology
from ..morphology.utilities import combine

from ..vla_complex_configurable.vla_complex_configurables.so101_manipulation_configurable import SO101ManipulationConfigurable
from ..vla_complex_configurable.vla_complex_configurables.ava_gen1_drive_configurable import AvaGen1DriveConfigurable
from ..vla_complex_configurable.vla_complex_configurable import VLA_Complex_Configurable

from vla_star.vla_star import VLA_Star

class MobileManipulatorConfigurable(VLA_Star_Configurable):
    def __init__(self,
        config: MobileManipulatorConfig,
        actuality: Actuality,
        morphology: Morphology,
        vla_complex_configurables: List[VLA_Complex_Configurable],
        name: str,
    ):
        super().__init__(
            config,
            actuality,
            morphology,
            vla_complex_configurables,
            name
        )

    def instantiate(self, **kwargs):
        context_engine = self.instantiate_with_filtered_args(self.config.instantiate, kwargs)

        vla_complexes = []
        for vla_complex_configurable in self.vla_complex_configurables:
            vla_complexes.append(self.instantiate_with_filtered_args(vla_complex_configurable.instantiate, kwargs))
        context_engine.link_vla_complexes(vla_complexes)
        return VLA_Star(context_engine, vla_complexes) 